import json
import os
from mvGen import move_generator
from myutils import setMajor, call_Snatch, checkPokerType, Num2Poker


_online = os.environ.get("USER", "") == "root"

# Read input
if _online:
    full_input = json.loads(input())
else:
    with open("input/log_forAI.json") as fo:
        full_input = json.load(fo)

curr_request = full_input["requests"][-1]

if curr_request["stage"] == "deal":
    # 发牌阶段 - 决定是否报/反
    get_card = curr_request["deliver"][0]

    # 还原当前手牌
    hold = []
    for i in range(len(full_input["requests"])):
        req = full_input["requests"][i]
        if req["stage"] == "deal":
            hold.extend(req["deliver"])

    called = curr_request["global"]["banking"]["called"]
    snatched = curr_request["global"]["banking"]["snatched"]
    level = curr_request["global"]["level"]
    major = curr_request["global"]["banking"]["major"]

    # 使用启发式策略决定是否报/反
    response = call_Snatch(get_card, hold[:-1], called, snatched, level, major)

elif curr_request["stage"] == "cover":
    # 埋牌阶段
    level = curr_request["global"]["level"]
    major = curr_request["global"]["banking"]["major"]
    setMajor(major, level)

    # 使用move_generator的启发式埋牌策略
    mv_gen = move_generator(level, major, full_input)
    response = mv_gen.cover_Pub()

elif curr_request["stage"] == "play":
    # 出牌阶段
    level = curr_request["global"]["level"]
    major = curr_request["global"]["banking"]["major"]
    setMajor(major, level)

    # 实例化move_generator（包含历史还原）
    mv_gen = move_generator(level, major, full_input)

    history_curr = curr_request["history"][1]

    # 使用纯启发式策略选择出牌
    if len(history_curr) == 0:
        # 首家出牌
        response = mv_gen.gen_one_action()
    else:
        # 跟牌
        first_move = history_curr[0]
        poktype = checkPokerType(first_move, level)

        if poktype == "single":
            # 单张跟牌
            response = mv_gen.gen_single_new(history_curr)
        elif poktype == "pair":
            # 对子跟牌
            response = mv_gen.gen_pair_new(history_curr)
        elif poktype == "tractor":
            # 拖拉机跟牌
            deck = [Num2Poker(p) for p in mv_gen.hold]
            tgt = [Num2Poker(p) for p in first_move]
            moves = mv_gen.gen_tractor(deck, tgt)
            response = moves[0] if moves else []
        elif poktype == "suspect":
            # 甩牌跟牌
            deck = [Num2Poker(p) for p in mv_gen.hold]
            tgt = [Num2Poker(p) for p in first_move]
            moves = mv_gen.gen_throw(deck, tgt)
            response = moves[0] if moves else []
        else:
            # 未知牌型，返回空
            response = []

# 输出JSON格式的响应
print(json.dumps({
    "response": response
}))

import torch
from collections import Counter

cardscale = ['A','2','3','4','5','6','7','8','9','0','J','Q','K']
suitset = ['s','h','c','d']
Major = ['jo', 'Jo']
pointorder = ['2','3','4','5','6','7','8','9','0','J','Q','K','A']
valuecards = ['5','0','K']

def setMajor(major, level):
    global Major
    if major != 'n': # 非无主
        Major = [major+point for point in pointorder if point != level] + [suit + level for suit in suitset if suit != major] + [major + level] + Major
    else: # 无主
        Major = [suit + level for suit in suitset] + Major
    pointorder.remove(level)
    
def Num2Poker(num): # num: int-[0,107]
    # Already a poker
    if type(num) is str and (num in Major or (num[0] in suitset and num[1] in cardscale)):
        return num
    # Locate in 1 single deck
    NumInDeck = num % 54
    # joker and Joker:
    if NumInDeck == 52:
        return "jo"
    if NumInDeck == 53:
        return "Jo"
    # Normal cards:
    pokernumber = cardscale[NumInDeck // 4]
    pokersuit = suitset[NumInDeck % 4]
    return pokersuit + pokernumber

def Poker2Num(poker, deck): # poker: str
    NumInDeck = -1
    if poker[0] == "j":
        NumInDeck = 52
    elif poker[0] == "J":
        NumInDeck = 53
    else:
        NumInDeck = cardscale.index(poker[1])*4 + suitset.index(poker[0])
    if NumInDeck in deck:
        return NumInDeck
    else:
        return NumInDeck + 54

def Poker2Num_seq(pokers, deck):
    id_seq = []
    deck_copy = deck + []
    for card_name in pokers:
        card_id = Poker2Num(card_name, deck_copy)
        id_seq.append(card_id)
        deck_copy.remove(card_id)
    return id_seq
    
def checkPokerType(poker, level): #poker: list[int]
    poker = [Num2Poker(p) for p in poker]
    if len(poker) == 1:
        return "single" #一张牌必定为单牌
    if len(poker) == 2:
        if poker[0] == poker[1]:
            return "pair" #同点数同花色才是对子
        else:
            return "suspect" #怀疑是甩牌
    if len(poker) % 2 == 0: #其他情况下只有偶数张牌可能是整牌型（连对）
    # 连对：每组两张；各组花色相同；各组点数在大小上连续(需排除大小王和级牌)
        count = Counter(poker)
        if "jo" in count.keys() and "Jo" in count.keys() and count['jo'] == 2 and count['Jo'] == 2:
            return "tractor"
        elif "jo" in count.keys() or "Jo" in count.keys(): # 排除大小王
            return "suspect"
        for v in count.values(): # 每组两张
            if v != 2:
                return "suspect"
        pointpos = []
        suit = list(count.keys())[0][0] # 花色相同
        for k in count.keys():
            if k[0] != suit or k[1] == level: # 排除级牌
                return "suspect"
            pointpos.append(pointorder.index(k[1])) # 点数在大小上连续
        pointpos.sort()
        for i in range(len(pointpos)-1):
            if pointpos[i+1] - pointpos[i] != 1:
                return "suspect"
        return "tractor" # 说明是拖拉机
    
    return "suspect"


def isMajor(card, major, level):
    return card[0] == major or card[1] == 'o' or card[1] == level

def card_level(card, major, level):
    if not isMajor(card, major, level):
        return pointorder.index(card[1])
    else:
        if card[1] == level:
            if card[0] == major:
                return 114
            else:
                return 113
        if card == "Jo":
            return 116
        if card == "jo":
            return 115
        return pointorder.index(card[1])+100
    
def divide_suit(tgt):
    #把某种花色分为单牌和对子
    singles = []
    pairs = []
    for card in tgt:
        #如果有两张
        if tgt.count(card) == 2 and card not in pairs:
            pairs.append(card)
        if card not in singles:
            singles.append(card)
    return singles, pairs

def divide_pairs(tgt,first_tractor_len,major,level):
    #从对子中提取拖拉机
    if (len(tgt)==0):
        return []
    elif (len(tgt)==1):
        return [tgt[0]+str(first_tractor_len)]
    elif (card_level(tgt[0],major,level)+1==card_level(tgt[1],major,level)):
        return divide_pairs(tgt[1:],first_tractor_len+1,major,level)
    elif (card_level(tgt[0],major,level)==card_level(tgt[1],major,level)):
        return divide_pairs(tgt[1:],first_tractor_len,major,level)
    else:
        return [tgt[0]+str(first_tractor_len)]+divide_pairs(tgt[1:],1,major,level)

def call_Snatch(get_card, deck, called, snatched, level):
# get_card: new card in this turn (int)
# deck: your deck (list[int]) before getting the new card
# called & snatched: player_id, -1 if not called/snatched
# level: level
# return -> list[int]
    response = []
## 目前的策略是一拿到牌立刻报/反，之后不再报/反
## 不反无主
    deck_poker = [Num2Poker(id) for id in deck]
    get_poker = Num2Poker(get_card)
    if get_poker[1] == level:
        if called == -1:
            response = [get_card]
        elif snatched == -1:
            if (get_card + 54) % 108 in deck:
                response = [get_card, (get_card + 54) % 108]
    return response


def cover_Pub(old_public, deck, major, level):
# old_public: raw publiccard (list[int])
    # 将old_public中的牌全部加入到deck中并转化为扑克格式
    """deck = deck + old_public
    deck_poker = [Num2Poker(id) for id in deck]
    # 整理各个花色的手牌
    suit_cards = {suit: [] for suit in suitset}
    suit_cards['n'] = []
    for card in deck_poker:
        if card[1] == 'o' or card[1] == level:
            suit_cards['n'].append(card)
        else:
            suit_cards[card[0]].append(card)"""


    
    # 去掉各个花色不打算埋的牌

    # 贪心地尽量埋尽可能多的花色

    return old_public

def playCard(history, hold, played, level, wrapper, mv_gen, model, selfid):
    # generating obs
    obs = {
        "id": selfid,
        "deck": [Num2Poker(p) for p in hold],
        "history": [[Num2Poker(p) for p in move] for move in history],
        "major": [Num2Poker(p) for p in Major],
        "played": [[Num2Poker(p) for p in cardset] for cardset in played]
    }
    # generating action_options
    action_options = get_action_options(hold, history, level, mv_gen) 
    #print(action_options)
    # generating state
    state = {}
    obs_mat, action_mask = wrapper.obsWrap(obs, action_options)
    state['observation'] = torch.tensor(obs_mat, dtype = torch.float).unsqueeze(0)
    state['action_mask'] = torch.tensor(action_mask, dtype = torch.float).unsqueeze(0)
    # getting actions
    action = obs2action(model, state)
    response = action_intpt(action_options[action], hold)
    return response


def get_action_options(deck, history, level, mv_gen):
    deck = [Num2Poker(p) for p in deck]
    if len(history) == 4 or len(history) == 0: # first to play
        #return mv_gen.gen_all(deck)
        return [mv_gen.gen_one_action()]
    else:
        tgt = [Num2Poker(p) for p in history[0]]
        poktype = checkPokerType(history[0], level)
        if poktype == "single":
            return mv_gen.gen_single(deck, tgt)
        elif poktype == "pair":
            return mv_gen.gen_pair(deck, tgt)
        elif poktype == "tractor":
            return mv_gen.gen_tractor(deck, tgt)
        elif poktype == "suspect":
            return mv_gen.gen_throw(deck, tgt)    

def obs2action(model, obs):
    model.train(False) # Batch Norm inference mode
    with torch.no_grad():
        logits, value = model(obs)
        action_dist = torch.distributions.Categorical(logits = logits)
        action = action_dist.sample().item()
    return action

def action_intpt(action, deck):
    '''
    interpreting action(cardname) to response(dick{'player': int, 'action': list[int]})
    action: list[str(cardnames)]
    '''
    action = Poker2Num_seq(action, deck)
    return action

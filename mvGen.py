from textwrap import indent
import numpy as np
from collections import Counter
from itertools import combinations
import myutil
class move_generator():
    def __init__(self, level, major,req=None):
        self.card_scale = myutil.cardscale
        self.suit_set = myutil.suitset
        self.point_order = myutil.pointorder
        self.value_cards = myutil.valuecards
        self.Major = myutil.Major
        self.major = major
        self.level = level
        
        # 初始化手牌、已打牌和剩余牌
        self.hold = []  # 玩家手牌
        self.played = [[], [], [], []]  # 每个玩家已打牌
        self.cards_left = []  # 剩余牌
        for i in range(108):
            self.cards_left.append(i)

        if req is not None:
            # 还原历史
            for i in range(len(req["requests"])):
                stage_req = req["requests"][i]
                if stage_req["stage"] == "deal":
                    self.hold.extend(stage_req["deliver"])
                    for card in stage_req["deliver"]:
                        self.cards_left.remove(card)
                elif stage_req["stage"] == "cover":
                    self.hold.extend(stage_req["deliver"])
                    for card in stage_req["deliver"]:
                        self.cards_left.remove(card)
                    action_cover = req["responses"][i]
                    for card in action_cover:
                        self.hold.remove(card)
                elif stage_req["stage"] == "play":
                    history = stage_req["history"]
                    selfid = (history[3] + len(history[1])) % 4
                    if len(history[0]) != 0:
                        self_move = history[0][(selfid - history[2]) % 4]
                        for card in self_move:
                            self.hold.remove(card)
                        for player_rec in range(len(history[0])):
                            self.played[(history[2] + player_rec) % 4].extend(history[0][player_rec])
                            if player_rec != (selfid - history[2]) % 4:
                                for card in history[0][player_rec]:
                                    self.cards_left.remove(card)
            # 还原当前请求
            curr_request = req["requests"][-1]
            if curr_request["stage"] == "play":
                his_current=curr_request["history"][1]
                for cards in his_current:
                    for card in cards:
                        self.cards_left.remove(card)
            self.organized_hold_cards = self.organize_cards(self.hold)
            self.organized_left_cards = self.organize_cards(self.cards_left)
    def isMajor(self, card):
        return myutil.isMajor(card,self.major,self.level)
    def card_level(self, card):
        return myutil.card_level(card,self.major,self.level)

    def organize_cards(self,cards):
        # 1. 将 hold 中的每张牌转化为扑克格式
        converted_cards = [self.Num2Poker(card) for card in cards]

        # 2. 按照主花色和副花色分类
        main_suit_cards = [card for card in converted_cards if self.isMajor(card)]
        other_suits_cards = {suit: [] for suit in self.suit_set if suit != self.major}

        for card in converted_cards:   
            if not self.isMajor(card):
                other_suits_cards[card[0]].append(card)

        # 3. 对每一类牌进行排序（按点数排序）
        main_suit_cards.sort(key=lambda x: self.card_level(x) )
        for suit in other_suits_cards:
            other_suits_cards[suit].sort(key=lambda x: self.card_level(x))

        major_single, major_pairs=self.divide_suit(main_suit_cards)

        major_tractors=self.divide_pairs(major_pairs,1)

        #移除长度为1的拖拉机
        major_tractors=[tractor for tractor in major_tractors if int(tractor[-1])>1]

        #把拖拉机按照长度排序
        major_tractors.sort(key=lambda x: int(x[-1]))

        main_suit_cards = {
            "singles": major_single,
            "pairs": major_pairs,
            "tractors": major_tractors
        }

        #按照长度排序
        other_suits_cards = sorted(other_suits_cards.items(), key=lambda item: len(item[1]))
        other_suits_cards = dict(other_suits_cards)

        for suit in other_suits_cards:
            singles, pairs=self.divide_suit(other_suits_cards[suit])
            tractors=self.divide_pairs(pairs,1)
            tractors=[tractor for tractor in tractors if int(tractor[-1])>1]
            tractors.sort(key=lambda x: int(x[-1]))
            other_suits_cards[suit] = {
                "singles": singles,
                "pairs": pairs,
                "tractors": tractors
            }
        return {
            "main_suit_cards": main_suit_cards,
            "other_suits_cards": other_suits_cards
        }
    def Num2Poker(self,num): # num: int-[0,107]
        return myutil.Num2Poker(num) 
        
    def gen_single(self, deck, tgt):
        '''
        deck: player's deck
        tgt: target cardset(list of cardnames)
        '''
        moves = []
        if tgt[0] in self.Major:
            moves = [[p] for p in deck if p in self.Major]
            if len(moves) == 0: # No Major in deck
                moves = [[p] for p in deck]
        else:
            moves = [[p] for p in deck if p[0] == tgt[0][0] and p not in self.Major]
            if len(moves) == 0:
                moves = [[p] for p in deck]
        
        return moves 
    
    
    def gen_pair(self, deck, tgt):
        '''
        deck: player's deck
        tgt: target cardset(list of cardnames)
        '''
        moves = []
        if tgt[0] in self.Major:
            sel_deck = [p for p in deck if p in self.Major]
        else:
            sel_deck = [p for p in deck if p[0] == tgt[0][0] and p not in self.Major]
        sel_count = Counter(sel_deck)
        for k,v in sel_count.items():
            if v == 2:
                moves.append([k, k])
        if len(moves) == 0:
            if len(sel_deck) >= 2: # Generating cardset with same suit
                for i in range(len(sel_deck)-1):
                    for j in range(len(sel_deck)-i-1):
                        moves.append([sel_deck[i], sel_deck[i+j+1]])
            elif len(sel_deck) == 1:
                move_uni = sel_deck
                for p in deck:
                    if p != move_uni[0]:
                        moves.append(move_uni+[p])
            else:
                deck_cnt = Counter(deck)
                for k, v in deck_cnt:
                    if v == 2:
                        moves.append([k, k])
                if len(moves) == 0:
                    for i in range(len(deck)-1):
                        for j in range(len(deck)-i-1):
                            moves.append([deck[i], deck[i+j+1]])        
        return moves
    
    def gen_tractor(self, deck, tgt):
        moves = []
        tractor_len = len(tgt)
        pair_cnt = tractor_len // 2
        if tgt[0] in self.Major:
            sel_deck = [p for p in deck if p in self.Major]
        else:
            sel_deck = [p for p in deck if p[0] == tgt[0][0] and p not in self.Major]
        
        sel_count = Counter(sel_deck)
        sel_pairs = [k for k, v in sel_count.items() if v == 2] # Is actually list of cardname
        if "jo" in sel_pairs and "Jo" in sel_pairs and tractor_len == 4:
            moves.append(["jo", "jo", "Jo", "Jo"])
        if tgt[0] in self.Major:
            if self.major != 'n':
                trac_pairs = [p for p in sel_pairs if p[0] == self.major and p[1] != self.level]
                trac_pairs.sort(key=lambda x: self.point_order.index(x[1]))
            else:
                trac_pairs = []
        else:
            trac_pairs = sel_pairs + []
            trac_pairs.sort(key=lambda x: self.point_order.index(x[1]))
            
        if len(sel_deck) < len(tgt): # attaching cards with other suits
            other_deck = [p for p in deck if p not in sel_deck]
            move_uni = sel_deck
            sup_sets = list(combinations(other_deck, len(tgt)-len(sel_deck)))
            for cardset in sup_sets:
                moves.append(move_uni+list(cardset))
        
        else:  # attaching cards with same suits
            if len(sel_pairs) < pair_cnt:
                move_uni = [p for k in sel_pairs for p in [k, k]]
                sup_singles = [p for p in sel_deck if p not in sel_pairs] # enough to make a cardset
                sup_sets = list(combinations(sup_singles, tractor_len - len(sel_pairs)*2))
                for cardset in sup_sets:
                    moves.append(move_uni + list(cardset))
            elif len(trac_pairs) < pair_cnt: # can be compensated with sel_pairs
                pair_sets = list(combinations(sel_pairs, tractor_len//2))
                for pairset in pair_sets:
                    moves.append([p for k in pairset for p in [k, k]])
            else:
                for i in range(len(trac_pairs)-pair_cnt+1): # Try to retrieve a tractor
                    if trac_pairs[i+pair_cnt-1][1] == self.point_order[self.point_order.index(trac_pairs[i][1])+pair_cnt-1]:
                        pair_set = [[trac_pairs[k], trac_pairs[k]] for k in range(i, i+pair_cnt)]
                        moves.append([p for pair in pair_set for p in pair])
                if len(moves) == 0:
                    pairsets = list(combinations(sel_pairs, tractor_len//2))
                    moves = [[p for k in pairset for p in [k, k]] for pairset in pairsets]
                    
        return moves  
                        
    def gen_throw(self, deck, tgt):
        level = self.level
        major = self.major
        outpok = []
        tgt_count = Counter(tgt)
        pos = []
        tractor = []
        suit = ''
        for k, v in tgt_count.items():
            if v == 2:
                if k != 'jo' and k != 'Jo' and k[1] != level: # 大小王和级牌当然不会参与拖拉机
                    pos.append(self.point_order.index(k[1]))
                    suit = k[0]
        if len(pos) >= 2:
            pos.sort()
            tmp = []
            suc_flag = False
            for i in range(len(pos)-1):
                if pos[i+1]-pos[i] == 1:
                    if not suc_flag:
                        tmp = [suit + self.point_order[pos[i]], suit + self.point_order[pos[i]], suit + self.point_order[pos[i+1]], suit + self.point_order[pos[i+1]]]
                        del tgt_count[suit + self.point_order[pos[i]]]
                        del tgt_count[suit + self.point_order[pos[i+1]]] # 已计入拖拉机的，从牌组中删去
                        suc_flag = True
                    else:
                        tmp.extend([suit + self.point_order[pos[i+1]], suit + self.point_order[pos[i+1]]])
                        del tgt_count[suit + self.point_order[pos[i+1]]]
                elif suc_flag:
                    tractor.append(tmp)
                    suc_flag = False
            if suc_flag:
                tractor.append(tmp)
        # 对牌型作基础的拆分 
        for k,v in tgt_count.items(): 
            outpok.append([k for i in range(v)])
        outpok.extend(tractor)
        
        moves = []
        move_uni = []
        self.reg_generator(deck, move_uni, outpok, moves)
        
        return moves


    def reg_generator(self, deck, move, outpok, moves):
        if len(outpok) == 0:
            moves.append(move)
            return
        tgt = outpok[-1] + []
        new_pok = outpok[:-1] + []
        if len(tgt) > 2:
            move_unis = self.gen_tractor(deck, tgt)
        elif len(tgt) == 2:
            move_unis = self.gen_pair(deck, tgt)
        elif len(tgt) == 1:
            move_unis = self.gen_single(deck, tgt)
        
        for move_uni in move_unis:
            new_move = move + move_uni
            new_deck = deck + []
            for p in move_uni:
                new_deck.remove(p)
            self.reg_generator(new_deck, new_move, new_pok, moves)
            
        return
    def get_shortest_other_suit(self,suits):
        #获得最短的非空副花色
        min_len = 100
        min_suit = ''
        for suit in suits:
            if len(self.organized_hold_cards["other_suits_cards"][suit]) < min_len :
                min_len = len(self.organized_hold_cards["other_suits_cards"][suit])
                min_suit = suit
        return min_suit, min_len
    def divide_suit(self, tgt):
        #把某种花色分为单牌和对子
        return myutil.divide_suit(tgt)

    
    def divide_pairs(self, tgt,first_tractor_len):
        #从对子中提取拖拉机：
        if (len(tgt)==0):
            return []
        elif (len(tgt)==1):
            return [tgt[0]+str(first_tractor_len)]
        elif (self.card_level(tgt[0])+1==self.card_level(tgt[1])):
            return self.divide_pairs(tgt[1:],first_tractor_len+1)
        elif (self.card_level(tgt[0])==self.card_level(tgt[1])):
            return self.divide_pairs(tgt[1:],first_tractor_len)
        else:
            return [tgt[0]+str(first_tractor_len)]+self.divide_pairs(tgt[1:],1)

    def is_largest_single(self, card):
        if self.isMajor(card):
            if len(self.organized_left_cards["main_suit_cards"]["singles"])==0 or self.card_level(card) >= self.card_level(self.organized_left_cards["main_suit_cards"]["singles"][-1]):
                return True
        else:
            if len(self.organized_left_cards["other_suits_cards"][card[0]]["singles"])==0 or self.card_level(card) >= self.card_level(self.organized_left_cards["other_suits_cards"][card[0]]["singles"][-1]):
                return True
        return False

    def is_largest_pair(self, card):
        if self.isMajor(card):
            if len(self.organized_left_cards["main_suit_cards"]["pairs"])==0 or self.card_level(card) >= self.card_level(self.organized_left_cards["main_suit_cards"]["pairs"][-1]):
                return True
        else:
            if len(self.organized_left_cards["other_suits_cards"][card[0]]["pairs"])==0 or self.card_level(card) >= self.card_level(self.organized_left_cards["other_suits_cards"][card[0]]["pairs"][-1]):
                return True
        return False
    def is_value(self, card):
        if card[1] in self.value_cards:
            return True
        else:   
            return False
    def tractor_to_action(self,tractor):
        action=[]
        len=int(tractor[-1])
        first_card=self.point_order.index(tractor[1])-len+1
        for i in range(len):
            action.append(tractor[0]+self.point_order[first_card+i])
            action.append(tractor[0]+self.point_order[first_card+i])
        return action
    
    def have_major(self):
        return len(self.organized_hold_cards["main_suit_cards"]["singles"])>0

    def play_major(self):   
        if self.have_major():
            #尝试出大对子
            if self.have_major_pair():
                return [self.organized_hold_cards["main_suit_cards"]["pairs"][-1],self.organized_hold_cards["main_suit_cards"]["pairs"][-1]]
            #尝试出小单张
            return [self.organized_hold_cards["main_suit_cards"]["singles"][0]]
        return []
    def play_other_suit(self,suit):
        if len(self.organized_hold_cards["other_suits_cards"][suit]["singles"])==0:
            return []
        largest_single = self.organized_hold_cards["other_suits_cards"][suit]["singles"][-1]
        if self.have_pair(suit):
            largest_pair = self.organized_hold_cards["other_suits_cards"][suit]["pairs"][-1]
            if self.is_largest_pair(largest_pair) and self.is_largest_single(largest_single):
                return [largest_pair,largest_pair,largest_single]
            if self.is_largest_pair(largest_pair):
                return [largest_pair,largest_pair]
        if self.is_largest_single(largest_single):
            return [largest_single]
        return []
    def play_major_tractor(self):
        if self.have_major_tractor():
            return self.tractor_to_action(self.organized_hold_cards["main_suit_cards"]["tractors"][-1])
        return []
    def play_tractor(self,suit):
        if self.have_tractor(suit):
            return self.tractor_to_action(self.organized_hold_cards["other_suits_cards"][suit]["tractors"][-1])
        return []
    def play_pair(self,suit):
        if self.have_pair(suit):
            largest_pair = self.organized_hold_cards["other_suits_cards"][suit]["pairs"][-1]
            return [largest_pair,largest_pair]
        return []
    
    def play_single(self,suit):
        if self.have_single(suit):
            largest_single = self.organized_hold_cards["other_suits_cards"][suit]["singles"][-1]
            return [largest_single]
        return []
    
    def have_major_tractor(self):
        return len(self.organized_hold_cards["main_suit_cards"]["tractors"])>0

    def have_tractor(self,suit):
        return len(self.organized_hold_cards["other_suits_cards"][suit]["tractors"])>0

    def have_major_pair(self):
        return len(self.organized_hold_cards["main_suit_cards"]["pairs"])>0
    
    def have_pair(self,suit):
        return len(self.organized_hold_cards["other_suits_cards"][suit]["pairs"])>0
    
    def have_major_single(self):
        return len(self.organized_hold_cards["main_suit_cards"]["singles"])>0

    def have_single(self,suit):
        return len(self.organized_hold_cards["other_suits_cards"][suit]["singles"])>0
    def gen_one_action(self):
        result=[]
        #查看是否有拖拉机：
        result=self.play_major_tractor()
        if len(result)>0:
            return result
        for suit in self.organized_hold_cards["other_suits_cards"]:
            result=self.play_tractor(suit)
            if len(result)>0:
                return result
        #如果没有拖拉机，从短往长出
        for suit in self.organized_hold_cards["other_suits_cards"]:
            result=self.play_other_suit(suit)
            if len(result)>0:
                return result

        #如果没有最大的对子和单牌，尝试出主
        result=self.play_major()
        if len(result)>0:
            return result
        #如果没有主，尝试出副对子
        for suit in self.organized_hold_cards["other_suits_cards"]:
            result=self.play_pair(suit)
            if len(result)>0:
                return result
        
        #如果没有副对子，尝试出副单牌
        for suit in self.organized_hold_cards["other_suits_cards"]:
            result=self.play_single(suit)
            if len(result)>0:
                return result

        #不应该到这里
        print("Error: No action generated") 
        return []


    def gen_all(self, deck): # Generating all cardset options
        moves = []
        suit_decks = []
        major_deck = [p for p in deck if p in self.Major]
        for i in range(4):
            suit_decks.append([p for p in deck if p[0] == self.suit_set[i] and p not in self.Major])
        # Do the major first
        major_count = Counter(major_deck)
        # Adding in all pairs and singles
        for k, v in major_count.items():
            if v == 1:
                moves.append([k])
            if v == 2:
                moves.append([k, k])
        # Adding in tractors
        if "jo" in major_count and major_count["jo"] == 2 and "Jo" in major_count and major_count["Jo"] == 2:
            moves.append(["jo", "jo", "Jo", "Jo"])
        trac_major = [k for k,v in major_count.items() if v == 2 and k[1] != self.level and k[1] != 'o']
        trac_major.sort(key=lambda x: self.point_order.index(x[1]))
        tracstreak = []
        for i in range(len(trac_major)):
            if len(tracstreak) == 0 or self.point_order.index(trac_major[i][1]) - self.point_order.index(tracstreak[-1][1]) > 1: # begin a new tracstreak
                tracstreak = [trac_major[i], trac_major[i]]
            else:
                tracstreak.extend([trac_major[i], trac_major[i]])
                moves.append(tracstreak+[])
                
        for suit_deck in suit_decks:
            suit_count = Counter(suit_deck)
            # Adding in all pairs and singles
            for k, v in suit_count.items():
                if v == 1:
                    moves.append([k])
                if v == 2:
                    moves.append([k, k])
            # Adding in tractors
            tracstreak = []
            trac_suit = [k for k,v in suit_count.items() if v==2]
            trac_suit.sort(key=lambda x: self.point_order.index(x[1]))
            for i in range(len(trac_suit)):
                if len(tracstreak) == 0 or self.point_order.index(trac_suit[i][1]) - self.point_order.index(tracstreak[-1][1]) > 1: # begin a new tracstreak
                    tracstreak = [trac_suit[i], trac_suit[i]]
                else:
                    tracstreak.extend([trac_suit[i], trac_suit[i]])
                    moves.append(tracstreak+[])
                    
        return moves
    
        
        
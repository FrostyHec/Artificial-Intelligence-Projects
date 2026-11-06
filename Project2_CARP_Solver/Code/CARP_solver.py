import copy
import heapq
import math
import multiprocessing
import random
import sys
import time
from multiprocessing import Process
from typing import IO, List, Tuple, Optional, Callable, Set, Dict


class Edge:
    '''
    无向边
    '''

    def __init__(self, vert1: int, vert2: int, cost: int, demand: int):
        self.vert1 = vert1  # 小顶点
        self.vert2 = vert2  # 大顶点
        self.cost = cost
        self.demand = demand

    @classmethod
    def fromString(cls, string: str):
        arr = string.split(' ')
        vals = []
        for e in arr:
            if e.strip() != '':
                vals.append(int(e))
        v1, v2, cost, demand = vals[0], vals[1], vals[2], vals[3]
        return cls(min(v1, v2), max(v1, v2), cost, demand)

    def __eq__(self, other) -> bool:
        return self.vert1 == other.vert1 and self.vert2 == other.vert2

    def __hash__(self) -> int:
        return hash((self.vert1, self.vert2))

    def beginAt(self, prev_end: int):
        return prev_end == self.vert1 or prev_end == self.vert2

    def getDirectedTuple(self, from_vertex: int) -> Tuple[int, int]:
        to_vertex = self.vert2 if self.vert1 == from_vertex else self.vert1
        return (from_vertex, to_vertex)

    @staticmethod
    def reverseEdgeTuple(e1: Tuple[int, int]) -> Tuple[int, int]:
        return (e1[1], e1[0])

    @staticmethod
    def convertToDefaultOrder(e: Tuple[int, int]) -> Tuple[int, int]:
        '''
        翻转回（小顶点，大顶点）的顺序
        :param e:
        :return:
        '''
        if e[0] > e[1]:
            return (e[1], e[0])
        return e

    def __str__(self):
        return str(((self.vert1, self.vert2), self.cost, self.demand))


class GraphData:
    def __init__(self,
                 name: str,
                 vertices: int,
                 depot: int,
                 required_edges: int,
                 non_required_edges: int,
                 vehicle: int,
                 capacity: int,
                 total_cost_required_edges: int,
                 edge_list: List[Edge]
                 ):
        # graph info
        self.name: str = name
        self.vertices: int = vertices
        self.depot: int = depot
        self.required_edges: int = required_edges
        self.non_required_edges: int = non_required_edges
        self.vehicle: int = vehicle
        self.capacity: int = capacity
        self.total_cost_required_edges: int = total_cost_required_edges
        self.edge_list: List[Edge] = edge_list

        # adjMatrix
        self.adjMatrix = None
        # demand hash table,必须是(小顶点，大顶点)
        self.demand_hash_table: Dict[Tuple[int, int], Edge] = self.__generateDemandHashTable()

    def __generateDemandHashTable(self) -> Dict[Tuple[int, int], Edge]:
        res = dict()
        for e in self.edge_list:
            res[(e.vert1, e.vert2)] = e
        return res

    @classmethod
    def extractData(cls, filename: str):
        obj = cls.__readData(filename)
        obj.adjMatrix = cls.__Floyd(obj.vertices, obj.edge_list)
        return obj

    @classmethod
    def __readData(cls, filename: str):
        with open(filename) as file:
            name = Utils.readOneStrPerLine(file)
            vertices = Utils.readOneIntPerLine(file)
            depot = Utils.readOneIntPerLine(file)
            required_edges = Utils.readOneIntPerLine(file)
            non_required_edges = Utils.readOneIntPerLine(file)
            vehicle = Utils.readOneIntPerLine(file)  # number of vehicle==number of routes
            capacity = Utils.readOneIntPerLine(file)
            total_cost_required_edges = Utils.readOneIntPerLine(file)

            # get graph
            edge_list = []
            total_edges = required_edges + non_required_edges
            _ = file.readline()
            for i in range(total_edges):
                edge_list.append(Edge.fromString(file.readline()))
            return cls(
                name,
                vertices,
                depot,
                required_edges,
                non_required_edges,
                vehicle,
                capacity,
                total_cost_required_edges,
                edge_list
            )

    @staticmethod
    def __Floyd(vertices_num: int, edge_list: List[Edge]):
        '''
        TODO Floyd最后可以用dijkstra做多源最短路改进，不过只有最多0.4->0.08s的改进,有一点点效果
        :param vertices_num:
        :param edge_list:
        :return:
        '''
        # t1 = time.time()
        edge_list = edge_list + [Edge(i, i, 0, 0) for i in range(1, vertices_num + 1)]
        n = vertices_num + 1
        matrix = [[Utils.INF for _ in range(n)] for _ in range(n)]
        for e in edge_list:
            matrix[e.vert1][e.vert2] = matrix[e.vert2][e.vert1] = e.cost
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    matrix[i][j] = min(matrix[i][j], matrix[i][k] + matrix[k][j])
        # print(f"{FLOYD TIME: time.time() - t1}")
        return matrix

    def getMinDistance(self, from_vertex: int, to_vertex: int) -> int:
        return self.adjMatrix[from_vertex][to_vertex]

    def getEdgeFromTuple(self, edge_tuple: Tuple[int, int]) -> Edge:
        edge_tuple = Edge.convertToDefaultOrder(edge_tuple)
        return self.demand_hash_table[edge_tuple]


class Path:
    def __init__(self):
        self.__edges: List[Tuple[int, int]] = []  # 元组，不包含起始与结束的0
        self.__cost: int = 0
        self.__load: int = 0

    def __len__(self) -> int:
        return len(self.__edges)

    def addTupleEdgeToBack(self, edge_tuple: Tuple[int, int], prev_node: int, graph_data: GraphData):
        edge = graph_data.getEdgeFromTuple(edge_tuple)
        self.addEdgeToBack(edge, edge_tuple[0], prev_node, graph_data.getMinDistance)

    def addEdgeToBack(self, edge: Edge, edge_start: int, prev_node: int, getMinDistance: Callable[[int, int], int]):
        self.__edges.append(edge.getDirectedTuple(edge_start))
        self.__cost += edge.cost + getMinDistance(prev_node, edge_start)
        self.__load += edge.demand

    def prevNode(self) -> Optional[int]:
        return None if len(self.__edges) == 0 else self.__edges[-1][1]

    def cost(self) -> int:
        return self.__cost

    def load(self) -> int:
        return self.__load

    def edges(self) -> Tuple[Tuple[int, int], ...]:
        '''
        dont do any modification on edges outside!
        :return:
        '''
        return tuple(self.__edges)

    def edge(self, i: int) -> Tuple[int, int]:
        '''
        get the edge with index i(i=0->first edge)
        :param i:
        :return:
        '''
        return self.__edges[i]

    def addBackDepot(self, depot: int, getMinDistance: Callable[[int, int], int]):
        self.__cost += getMinDistance(self.__edges[-1][1], depot)

    def getRepresentation(self) -> Tuple[Tuple[Tuple[int, int], ...], int, int]:
        return tuple(self.__edges), self.__cost, self.__load

    def removeEdge(self, edge_idx: int, graph_data: GraphData) -> float:
        '''
        remove edge with edge idx( idx=0, remove first)
        :param edge_idx:
        :return:cost diff after remove
        '''
        if not 0 <= edge_idx < len(self):
            raise Exception('Invalid edge idx!')
        prev_end: int = graph_data.depot
        next_start: int = graph_data.depot
        edge: Tuple[int, int] = self.__edges[edge_idx]
        if edge_idx != 0:  # prev not depot
            prev_end = self.__edges[edge_idx - 1][1]
        if edge_idx != len(self) - 1:
            next_start = self.__edges[edge_idx + 1][0]

        # calculate new cost
        new_con_diff = graph_data.getMinDistance(prev_end, next_start)
        rmv_diff1 = graph_data.getMinDistance(prev_end, edge[0])
        rmv_diff2 = graph_data.getMinDistance(edge[1], next_start)
        edge_info = graph_data.getEdgeFromTuple(edge)
        total_diff = new_con_diff - rmv_diff1 - rmv_diff2 - edge_info.cost
        self.__cost += total_diff
        # calculate new load
        self.__load -= edge_info.demand
        # delete edge
        del self.__edges[edge_idx]
        return total_diff

    def insertEdge(self, edge_idx: int, edge: Tuple[int, int], graph_data: GraphData) -> float:
        '''
        在idx位置后面插入一个边，比如idx=0则插在第0个后面（也就是第一个），idx=1则插在第1个后面（也就是第二个）,也就是idx前面
        :param edge_idx:
        :param edge:
        :return: cost diff after adding
        '''
        if not 0 <= edge_idx <= len(self):
            raise Exception('Invalid edge idx!')
        prev_end: int = graph_data.depot
        next_start: int = graph_data.depot
        if edge_idx != 0:  # prev not depot
            prev_end = self.__edges[edge_idx - 1][1]
        if edge_idx != len(self):
            next_start = self.__edges[edge_idx][0]

        # calculate new cost
        rmv_diff = graph_data.getMinDistance(prev_end, next_start)
        ist_diff1 = graph_data.getMinDistance(prev_end, edge[0])
        ist_diff2 = graph_data.getMinDistance(edge[1], next_start)
        edge_info = graph_data.getEdgeFromTuple(edge)
        total_diff = -rmv_diff + ist_diff1 + ist_diff2 + edge_info.cost
        self.__cost += total_diff

        # calculate new load
        self.__load += edge_info.demand
        # insert edge
        self.__edges.insert(edge_idx, edge)
        return total_diff

    # def equals(self, given: Tuple[Tuple[Tuple[int, int], ...], int, int]) -> bool:  # TODO eq might redundant
    #     if len(given) != 3:
    #         return False
    #     return self.__edges == given[0] and self.__cost == given[1] and self.__load == given[2]

    def __str__(self):
        return str((self.__cost, self.__load, self.__edges))


class Solution:
    def __init__(self, paths: List[Path]):
        self.paths: List[Path] = paths
        self.total_cost = self.evaluate_solution(paths)

    @staticmethod
    def evaluate_solution(paths: List[Path]) -> int:
        return sum([p.cost() for p in paths])

    def getRepresentation(self) -> tuple:
        '''
        getRepresentation will return unique representation of a solution in tuple
        :return:
        '''
        return tuple([e.getRepresentation() for e in self.paths])

    def __lt__(self, other) -> bool:
        if math.isclose(self.total_cost, other.total_cost):
            return random.random() < 0.5  # TODO 同reward的不做比较

        return self.total_cost < other.total_cost

    def __str__(self):
        return str((self.total_cost, self.getRepresentation()))

    # def equals(self, given: tuple) -> bool:
    #     if len(given) != len(self.paths):
    #         return False
    #     for i in range(len(given)):
    #         if not self.paths[i].equals(given[i]):
    #             return False
    #     return True
    def removePathIfEmpty(self, x: int):
        if len(self.paths[x]) == 0:
            del self.paths[x]


######################################################不改动上面的类#####################################################


class Configuration:
    banPSStrategy = True
    logAll = False
    psRandom = 6  # 必须要>psType
    psType = 5
    totalPsType = psType + 1  # 包括random
    randomTime = 5
    msMaxDuplicateCnt = 5
    singleMSTime = 100
    maxLocalSearch = 100
    timeDif: float = 3  # Time dif between really used and time limit in secs.
    Pls: float = 0.2  # Pls params
    psize: int = 30  # 500  # population size
    ubtrail: int = 30  # unsuccessful attempts to gen new individual
    multiThreads = False
    multiThreadsTimeDif = 1.5


class Populations:
    # 实现了数个接口的数据结构
    # TODO 数据结构优化
    def __init__(self):
        self.arr: List[Solution] = []
        self.hash_set: Set[tuple] = set()

    def __len__(self):
        return len(self.arr)

    def __contains__(self, s: Solution) -> bool:
        return s.getRepresentation() in self.hash_set

    def add(self, s: Solution):
        heapq.heappush(self.arr, s)
        self.hash_set.add(s.getRepresentation())

    def getBest(self) -> Solution:
        return self.arr[0]

    def randomSelect2(self) -> Tuple[Solution, Solution]:
        return (self.arr[0],
                self.arr[random.randint(1, len(self.arr) - 1)])
        # x1, x2 = Utils.randomDifferent2(len(self.arr))
        # return self.arr[x1], self.arr[x2]

    def shrunk(self):
        # TODO shrunk to the target size
        pass

    def popBest(self) -> Solution:
        return heapq.heappop(self.arr)


class PathScanning:
    # TODO 在优化版本中，使用一组优先队列去维护unserved（优化版本）【其实可能不会显著提升性能】
    def __init__(self, graph_data: GraphData,
                 task: List[Tuple[int, int]] = None,
                 type: int = Configuration.psRandom
                 ):
        self.graph_data = graph_data  # copy by itself
        self.demand_edges: set[Edge] = self.__getDemandEdge(
            graph_data.edge_list.copy() if task is None
            else [graph_data.getEdgeFromTuple(e) for e in task]
        )
        self.max_capacity = graph_data.capacity
        self.start = graph_data.depot
        self.getMinDistance: Callable[[int, int], int] = graph_data.getMinDistance
        self.type = type

    def __getDemandEdge(self, edge_list: List[Edge]) -> Set[Edge]:
        res = set()
        for e in edge_list:
            if e.demand != 0:
                res.add(e)
        return res

    def getResult(self) -> Solution:
        result = []
        while self.__haveUnserved():
            path = Path()
            while self.__addPath(path):  # 循环添加边
                pass
            path.addBackDepot(self.start, self.getMinDistance)
            result.append(path)
        return Solution(result)

    def __haveUnserved(self) -> bool:
        return len(self.demand_edges) > 0

    def __addPath(self, path: Path) -> bool:  # return success or not
        prev_end = Utils.getWithDefault(path.prevNode(), self.start)
        candidate_list: List[Tuple[Edge, int]] = []
        min_distance = Utils.INF
        distance_to_depot, demand_vs_cost = None, None

        for e in self.demand_edges:
            if path.load() + e.demand <= self.max_capacity:  # TODO 为什么这么移效果会变好？
                # get edge entry direction
                dis1, dis2 = self.getMinDistance(prev_end, e.vert1), self.getMinDistance(prev_end, e.vert2)
                if dis1 > dis2:
                    cur_distance = dis2
                    start_pos = e.vert2
                else:
                    cur_distance = dis1
                    start_pos = e.vert1

                candidate = (e, start_pos)
                # greedily select min distance
                if min_distance > cur_distance:
                    candidate_list = [candidate]
                    min_distance = cur_distance
                elif min_distance == cur_distance:
                    if Configuration.banPSStrategy:
                        self.type = Configuration.psRandom
                    # TODO 复制就复制吧有必要再改
                    if self.type == 1:  # maximize distance to depot
                        val = self.getMinDistance(self.start, start_pos)
                        if distance_to_depot is None or distance_to_depot < val:
                            distance_to_depot = val
                            candidate_list = [candidate]
                        elif distance_to_depot == val:
                            candidate_list.append(candidate)

                    elif self.type == 2:
                        val = self.getMinDistance(self.start, start_pos)
                        if distance_to_depot is None or distance_to_depot > val:
                            distance_to_depot = val
                            candidate_list = [candidate]
                        elif distance_to_depot == val:
                            candidate_list.append(candidate)

                    elif self.type == 3:
                        val = e.demand / e.cost
                        if demand_vs_cost is None or demand_vs_cost < val:
                            demand_vs_cost = val
                            candidate_list = [candidate]
                        elif distance_to_depot == val:
                            candidate_list.append(candidate)

                    elif self.type == 4:
                        val = e.demand / e.cost
                        if demand_vs_cost is None or demand_vs_cost > val:
                            demand_vs_cost = val
                            candidate_list = [candidate]
                        elif distance_to_depot == val:
                            candidate_list.append(candidate)

                    elif self.type == 5:
                        if path.load() < self.max_capacity / 2:
                            val = self.getMinDistance(self.start, start_pos)
                            if distance_to_depot is None or distance_to_depot < val:
                                distance_to_depot = val
                                candidate_list = [candidate]
                            elif distance_to_depot == val:
                                candidate_list.append(candidate)
                        else:
                            val = self.getMinDistance(self.start, start_pos)
                            if distance_to_depot is None or distance_to_depot > val:
                                distance_to_depot = val
                                candidate_list = [candidate]
                            elif distance_to_depot == val:
                                candidate_list.append(candidate)

                    else:
                        if Configuration.psRandom != self.type:
                            raise 'Error implementation!'
                        candidate_list.append(candidate)

                # print(f'{(str(e),start_pos)} with distance:{cur_distance}')
                # print(f'after edge e:{e}, min_distance:{min_distance},candidate:{[(str(e[0]),e[1]) for e in candidate]}')

        if min_distance == Utils.INF:  # no possible edge
            return False

        # if self.type!=Configuration.psRandom and len(candidate_list)>1:
        #     print(f'Non random type with multiple candidate! type:{self.type}, with len:{len(candidate_list)}')
        # TODO five kind approach
        choice: Tuple[Edge, int] = random.choice(candidate_list)
        # if path.load() + choice[0].demand > self.max_capacity:
        #     return False
        # print(f'Selected:{(str(choice[0]),choice[1])}')
        # add res
        path.addEdgeToBack(choice[0], choice[1], prev_end, self.getMinDistance)
        self.demand_edges.remove(choice[0])
        return True


class Solver:
    def __init__(self, graph_data: GraphData, shared_dict=None):
        self.__graph_data: Optional[GraphData] = graph_data
        self.__result_dict = dict() if shared_dict is None else shared_dict
        self.__tabu_list: Set[tuple] = set()  # representation
        self.__optimal_pos: Populations = Populations()

    def getResult(self) -> Solution:
        return self.__result_dict['result']

    def __setResult(self, s: Solution) -> None:
        self.__result_dict['result'] = s

    def solve(self, time_limit: float) -> None:
        '''
        这一个版本为:对于每个个体使用ls操作搜索到它的最优解，达到最优解后切换个体，如果所有个体都都跑完了就跑交叉
        现在倒不是严格地逐次挑选最优
        :param time_limit:
        :return:
        '''
        pops = self.__initSolution()
        self.__setResult(pops.getBest())
        if len(pops) < 2:
            print('Too less populations!')
            raise 'ERR'
        start = time.time()
        loop_cnt = 0
        tabu_cnt = 0
        while time.time() - start < time_limit - Configuration.timeDif:  # TODO Stopping criterion(x duplicate?
            if Configuration.logAll:
                print(f'Time{loop_cnt} start')
                loop_cnt += 1

            if len(pops) <= 2:
                if Configuration.logAll:
                    print('=======================Every population has been tested=======================')
                break

            s1, s2 = pops.randomSelect2()
            sx = self.__mutate(s1, s2)
            if Configuration.logAll:
                print(f'selected:{sx}')
            cnt, prev_best = 0, sx.total_cost
            while cnt < 1:
                sls = self.__localSearch(sx)

                if sls.getRepresentation() in self.__tabu_list and Configuration.logAll:  # 直接禁忌 TODO tabu in ls is useless?
                    tabu_cnt += 1
                    print(f'Tabu hits with time {tabu_cnt}')
                    # break

                if prev_best > sls.total_cost:
                    prev_best = sls.total_cost
                    sx = sls
                else:
                    cnt += 1
            if Configuration.logAll:
                print('===========An local optimal occurs!================')
                print(sls)
            self.__tabu_list.add(sls.getRepresentation())
            self.__optimal_pos.add(pops.popBest())
            pops.shrunk()
            if self.getResult().total_cost > sls.total_cost:
                self.__setResult(sls)
            # r = random.random()  # [0,1)
            # if r < Configuration.Pls:
            #     sls = self.__localSearch(sx)
            #     if sls not in pops:
            #         pops.add(sls)
            #     elif sx not in pops:
            #         pops.add(sx)
            # elif sx not in pops:
            #     pops.add(sx)

    def __initSolution(self) -> Populations:
        # TODO 对于指定的type，一般candidate可能都不是特别多，可以设置一个ban操作，当策略无法对该种群改造出新结果时就跳过它
        '''
        当前这个搜索算法为贪心
        :return:
        '''
        pops = Populations()
        while len(pops) < Configuration.psize:
            ntrail = 0
            no_new = False
            while True:
                s = PathScanning(self.__graph_data,
                                 type=((len(pops) + ntrail) % Configuration.totalPsType + 1)
                                 ).getResult()
                if s not in pops:
                    pops.add(s)
                    break
                ntrail += 1
                if ntrail >= Configuration.ubtrail:
                    no_new = True
                    break
            if no_new:
                if Configuration.logAll:
                    print(f'Warning: nothing new, shrinking to {len(pops)}')
                break
            if len(pops) % 10 == 0 and Configuration.logAll:
                print(f'The {len(pops)} th with best:{pops.getBest()}')
        # print(f'Print top 3')
        # for i in range(3):
        #     print(pops.arr[i])
        return pops

    def __mutate(self, s1: Solution, s2: Solution) -> Optional[Solution]:
        '''
        :param s1:
        :param s2:
        :return:
        '''
        # if random.random() < 0.5:
        #     return s1
        # else:
        #     return s2
        # TODO crossover
        # I really wondered the effectiveness of the crossover steps, 这个交叉操作很可能不能产生什么有意义的解，而且很可能不快，为什么不直接做一些 large step的crossover? 或者干脆用Tabu Search?
        selected = random.choice([s1, s2])
        r = random.random()
        return selected
        # if r < 0.6:
        #     return selected
        # elif r < 0.8 and len(self.__optimal_pos) > 0:
        #     return self.__crossover(random.choice(self.__optimal_pos.arr), selected)
        # else:
        #     return self.__crossover(s1, s2)
        # if s1.getRepresentation() in self.__tabu_list:
        #     if s2.getRepresentation() in self.__tabu_list:
        #         return None
        #     else:
        #         return s2
        # else:
        #     return s1

    def __crossover(self, s1: Solution, s2: Solution) -> Solution:
        def split_route(r: Path) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
            i = random.randint(0, len(r) - 1)
            i = random.randint(0, len(r) - 1)
            r_l, r_r = list(r.edges())[:i], list(r.edges())[i:]
            return r_l, r_r

        rnd_path_idx = random.randint(0, len(s1.paths) - 1)
        s_x: Solution = Utils.deepcopy(s1)
        r_1, r_2 = s1.paths[rnd_path_idx], s2.paths[rnd_path_idx]
        r_11, r_12 = split_route(r_1)
        r_21, r_22 = split_route(r_2)

        r_new = r_11
        missing = set(r_12)
        duplicate = set(r_11)

        for itm in r_22:
            if itm in missing:
                r_new.append(itm)
                missing.remove(itm)
            elif itm in duplicate:
                pass  # ignore
            else:
                pass  # not in this set

        path_new = Path()
        prev_end = self.__graph_data.depot
        for tup in r_new:
            path_new.addTupleEdgeToBack(tup, prev_end, self.__graph_data)
            prev_end = tup[1]

        for edge_tup in missing:
            min_increase, best_idx = Utils.INF, 0
            for idx in range(len(path_new) + 1):
                p0: Path = Utils.deepcopy(path_new)
                cur_increase = path_new.insertEdge(idx, edge_tup, self.__graph_data)
                if cur_increase < min_increase:
                    min_increase, best_idx = cur_increase, idx
                path_new.removeEdge(idx, self.__graph_data)
                assert p0.edges() == path_new.edges()
            t1 = path_new.insertEdge(best_idx, edge_tup, self.__graph_data)
            assert min_increase == t1
        if Configuration.logAll:
            print(f'==============Old cost: {r_1.cost()},new cost: {path_new.cost()}=================')
            assert set(r_1.edges())==set(path_new.edges())
        s_x.paths[rnd_path_idx] = path_new
        s_x.total_cost+=(path_new.cost()-r_1.cost())
        return s_x
    def __localSearch(self, s: Solution) -> Solution:
        '''
        TODO 魔改版本可以把local search的中间解都塞到pops里，也可以在每一组的搜索中让small search和big search都试一试看看哪个好
        :param s:
        :return:
        '''
        # Doesn't introduce invalid solution, thus no need to use lambda
        cnt, res = 0, s
        while cnt < Configuration.maxLocalSearch:
            cnt += 1
            res = self.__smallStepOperations(res)
            lg_best = self.__largeStepOperations(res)  # TODO 尝试是否能jump out the local optima
            if lg_best is None:
                break
            # if lg_best.getRepresentation() in self.__tabu_list:
            #     print('Tabu hit in lg_best!!')
            #     return res
            self.__tabu_list.add(res.getRepresentation())
            self.__tabu_list.add(lg_best.getRepresentation())
            res = lg_best
        return res

    def __largeStepOperations(self, s: Solution) -> Optional[Solution]:
        # return s
        return self.__msOperator(s)

    def __msOperator(self, s: Solution) -> Optional[Solution]:
        '''
        TODO: 如果需要tabu list,这里需要修改
        :param s:
        :return:
        '''
        tested_normal = set()  # 试过基本五策略的
        tested_pool = set()  # str representation of tested part solution
        duplicateCnt = 0
        if len(s.paths) < 2:
            return s
        for i in range(Configuration.singleMSTime):
            choice = Utils.getAscTuple2(Utils.randomDifferent2(len(s.paths)))
            x1, x2 = choice
            p1, p2 = s.paths[x1], s.paths[x2]
            parted_task = list(p1.edges()) + list(p2.edges())
            origin_cost = p1.cost() + p2.cost()
            # TODO 可以考虑添加一条random check避免某一组choice被random太多次,可能也不一定需要
            if choice in tested_normal:
                part_solutions = [
                    PathScanning(self.__graph_data, parted_task, Configuration.psRandom).getResult()
                    for _ in range(Configuration.randomTime)
                ]
            else:
                tested_normal.add(choice)
                part_solutions = [
                    PathScanning(self.__graph_data, parted_task, t + 1).getResult()
                    for t in range(Configuration.psType)
                ]
            # get best part solution
            best, new_cost = None, Utils.INF
            for ps in part_solutions:
                if ps.total_cost < new_cost:
                    # TODO test insert_____
                    # new_x: Solution = Utils.deepcopy(s)
                    # new_x.paths[x1] = ps.paths[0]
                    # new_x.paths[x2] = ps.paths[1]
                    # if new_x.getRepresentation() in self.__tabu_list:
                    #     print('Tabu hit in ms!')
                    #     continue
                    new_cost = ps.total_cost
                    best = ps
            if best is None:
                return None
            best_hash = best.getRepresentation()
            if best_hash in tested_pool:
                duplicateCnt += 1
            tested_pool.add(best_hash)
            if duplicateCnt > Configuration.msMaxDuplicateCnt:
                if Configuration.logAll:
                    print(f'Early stop with time{i}')
                break
            if new_cost < origin_cost:
                # 可以返回一个很好的solution了
                new_s: Solution = Utils.deepcopy(s)
                new_s.paths[x1] = best.paths[0]
                new_s.paths[x2] = best.paths[1]
                new_s.total_cost -= (origin_cost - new_cost)  # TODO CHECK CORRECTNESS
                if Configuration.logAll:
                    print(f'New solutions in MS with cost {new_s.total_cost}, stop at:{i} ')
                return new_s
        return None

    def __smallStepOperations(self, s: Solution) -> Solution:
        '''
        如果这几个small step op都加入的话是否会更好？
        :param s:
        :return:
        '''
        # t1 = time.time()
        candidate: List[Solution] = [
            self.__singleInsertion(s),
            # self.__doubleInsertion(s),
            # self.__swap(s) #TODO, very interesting, swap is never better than single insertion
        ]
        # t2 = time.time()
        # print(f'耗费时间：{t2 - t1}')
        best_candidate: Solution = candidate[0]
        for s in candidate:
            if s.total_cost < best_candidate.total_cost:
                best_candidate = s

        # if best_candidate.getRepresentation() in self.__tabu_list:
        #     print('Returning swap!')
        #     return self.__swap(s)
        return best_candidate

    def __singleInsertion(self, s: Solution) -> Solution:
        '''
        O(n^2)=>5000个操作大约在0.005-0.01s
        Effective operator, but it will lead to local optimal
        :param s:
        :return:
        '''
        s_t: Solution = Utils.deepcopy(s)
        min_reduce_cost = 0  # 操作最多可以减少多少的cost(是个负数)
        insertion_way: Tuple[int, int, int, int, bool] = (0, 0, 0, 0, False)
        # foreach all insertion
        for x in range(len(s.paths)):
            path = s_t.paths[x]
            for i in range(len(path)):
                task = path.edge(i)  # 选择一条边，尝试插入任何其他地方看看是否会减小cost
                remove_diff = path.removeEdge(i, self.__graph_data)
                for y in range(len(s.paths)):
                    to_insert_path = s_t.paths[y]
                    for j in range(len(to_insert_path)):
                        if self.capableToInsert(to_insert_path, task):
                            updated, old_cost, old_ist_way = False, min_reduce_cost, insertion_way
                            # 正向
                            insert_diff = to_insert_path.insertEdge(j, task, self.__graph_data)  # 尝试插入
                            div = remove_diff + insert_diff
                            if div <= min_reduce_cost:  # cost less
                                min_reduce_cost = div
                                insertion_way = (x, i, y, j, False)
                                updated = True
                            to_insert_path.removeEdge(j, self.__graph_data)  # 恢复插入前

                            # swap方向
                            insert_diff2 = to_insert_path.insertEdge(j, Edge.reverseEdgeTuple(task), self.__graph_data)
                            div = remove_diff + insert_diff2
                            if div <= min_reduce_cost:
                                min_reduce_cost = div
                                insertion_way = (x, i, y, j, True)
                                updated = True
                            to_insert_path.removeEdge(j, self.__graph_data)  # 恢复插入前

                            # TODO test insert_____
                            # if updated:
                            #     x, i, y, j, reversed = insertion_way
                            #     str=s.getRepresentation()
                            #     tsk2: Tuple[int, int] = s.paths[x].edge(i)
                            #     s.paths[x].removeEdge(i, self.__graph_data)
                            #     s.removePathIfEmpty(x)
                            #     if reversed:
                            #         tsk2 = Edge.reverseEdgeTuple(tsk2)
                            #     s.paths[y].insertEdge(j, tsk2, self.__graph_data)
                            #     if s.getRepresentation() in self.__tabu_list:
                            #         # print('Tabu hit in single insertion!')
                            #         min_reduce_cost=old_cost
                            #         insertion_way=old_ist_way
                            #
                            #     s.paths[y].removeEdge(j, self.__graph_data)
                            #     s.paths[x].insertEdge(i, tsk2 if not reversed else Edge.reverseEdgeTuple(tsk2), self.__graph_data)
                            #     str2=s.getRepresentation()
                            #     if str!=str2:
                            #         raise 'ERR'

                path.insertEdge(i, task, self.__graph_data)  # 恢复这条边
        # insert edge to gen solution: make edge modification and update cost!
        x, i, y, j, reversed = insertion_way
        task: Tuple[int, int] = s_t.paths[x].edge(i)
        s_t.paths[x].removeEdge(i, self.__graph_data)
        s_t.removePathIfEmpty(x)
        if reversed:
            task = Edge.reverseEdgeTuple(task)
        s_t.paths[y].insertEdge(j, task, self.__graph_data)
        s_t.total_cost += min_reduce_cost

        if Configuration.logAll:
            if min_reduce_cost < 0:
                print(f'New changed in SingleInsertion!:s:{s_t.total_cost} with insertion way:{insertion_way}')
        return s_t

    def __doubleInsertion(self, s: Solution) -> Solution:
        '''
        这个可能还真有用，因为两条路径之间可能有一些较优结构
        吗？我又有点表示怀疑（
        :param s:
        :return:
        '''
        s_t = Utils.deepcopy(s)
        return s_t

    def __swap(self, s: Solution) -> Solution:
        '''
        TODO swap里面疑似算错值了
        TODO 基于__singleInsertion的改动，如果single改了这个也要改
        这个的const比较高 大约到0.02s
        :param s:
        :return:
        '''
        s_t: Solution = Utils.deepcopy(s)
        min_reduce_cost = 0  # 操作最多可以减少多少的cost(是个负数)
        insertion_way: Tuple[int, int, int, int, bool, bool] = (-1, -1, -1, -1, False, False)
        # foreach all insertion
        for x in range(len(s.paths)):
            path_i = s_t.paths[x]
            for i in range(len(path_i)):
                task_i = path_i.edge(i)  # 选择一条边，尝试插入任何其他地方看看是否会减小cost
                remove_i_diff = path_i.removeEdge(i, self.__graph_data)
                for y in range(i, len(s.paths)):  # TODO 避免(A,B) (B,A) 这样的无趣组合，对于(A,A)? I have no idea, maybe better
                    path_j: Path = s_t.paths[y]
                    for j in range(len(path_j)):
                        task_j = path_j.edge(j)
                        if task_i == task_j:
                            # TODO 没有必要尝试self-swap，这是由于在初始构造时，已经检查过swap后不会更好
                            continue
                        remove_j_diff = path_j.removeEdge(j, self.__graph_data)
                        if self.capableToInsert(path_j, task_i) and self.capableToInsert(path_i, task_j):
                            # i j的四个方向
                            test_pair = []
                            for reverse_i in [False, True]:
                                for reverse_j in [False, True]:
                                    task_ti = Edge.reverseEdgeTuple(task_i) if reverse_i else task_i
                                    task_tj = Edge.reverseEdgeTuple(task_j) if reverse_j else task_j
                                    test_pair.append((task_ti, task_tj, reverse_i, reverse_j))

                            for pair in test_pair:
                                cur_task_i, cur_task_j, reverse_i, reverse_j = pair
                                # 尝试交换插入
                                insert_j_diff = path_j.insertEdge(j, cur_task_i, self.__graph_data)
                                insert_i_diff = path_i.insertEdge(i, cur_task_j, self.__graph_data)
                                div = remove_i_diff + remove_j_diff + insert_i_diff + insert_j_diff
                                if div <= min_reduce_cost:  # cost less
                                    min_reduce_cost = div
                                    insertion_way = (x, i, y, j, reverse_i, reverse_j)
                                path_i.removeEdge(i, self.__graph_data)
                                path_j.removeEdge(j, self.__graph_data)  # 恢复插入前

                        path_j.insertEdge(j, task_j, self.__graph_data)
                path_i.insertEdge(i, task_i, self.__graph_data)  # 恢复这条边

        # insert edge to gen solution: make edge modification and update cost!
        x, i, y, j, reverse_i, reverse_j = insertion_way
        if x == -1:
            return s
            # 移除和插入必须按照顺序：移除i,j,插入j,i
        task_i: Tuple[int, int] = s_t.paths[x].edge(i)
        xa = s_t.paths[x].removeEdge(i, self.__graph_data)
        if reverse_i:
            task_i = Edge.reverseEdgeTuple(task_i)

        task_j: Tuple[int, int] = s_t.paths[y].edge(j)
        if reverse_j:
            task_j = Edge.reverseEdgeTuple(task_j)
        xb = s_t.paths[y].removeEdge(j, self.__graph_data)

        xc = s_t.paths[y].insertEdge(j, task_i, self.__graph_data)

        xd = s_t.paths[x].insertEdge(i, task_j, self.__graph_data)

        assert xa + xb + xc + xd == min_reduce_cost

        s_t.total_cost += min_reduce_cost
        if min_reduce_cost < 0 and Configuration.logAll:
            print(f'New changed in Swap!:s:{s_t.total_cost}, swap:{insertion_way}')
        if x == y and i == j and reverse_i == reverse_j:
            assert s == s_t
        # print(f'Returning new swap:{min_reduce_cost},{insertion_way}')
        return s_t

    def capableToInsert(self, path: Path, task: Tuple[int, int]) -> bool:
        return path.load() + self.__graph_data.getEdgeFromTuple(task).demand <= self.__graph_data.capacity


def threadStart(shared_dict):
    if Configuration.logAll:
        print('MultiThread start')
    solver: Solver = shared_dict['Solver']  # pickle.load(shared_dict['Solver'])
    solver.solve(100000000000)


class RunSolver:  # TODO run solver
    @staticmethod
    def solve(graph_data: GraphData, time_limit: float) -> Solution:
        # TODO 多进程
        # 多个进程初始化不同的种群并开始搜索，并共享一个解池，使用类似于禁忌搜索的方法，其他线程回避共享解池中已有(by hash)且非本线程的解
        # 多进程的时候一定要小心random的实现！
        if Configuration.multiThreads:
            with multiprocessing.Manager() as manager:
                shared_dict = manager.dict()
                shared_dict['Solver'] = Solver(graph_data, shared_dict)  # pickle.dump(Solver(graph_data, shared_dict))
                p = Process(target=threadStart, args=(shared_dict,))
                p.start()
                p.join(time_limit - Configuration.multiThreadsTimeDif)
                p.terminate()
                result = shared_dict['result']
            return result
        else:
            solver = Solver(graph_data)
            solver.solve(time_limit)
            return solver.getResult()

    # @staticmethod
    # def __threadStart(shared_dict):
    #     solver: Solver = shared_dict['Solver']#pickle.load(shared_dict['Solver'])
    #     solver.solve(100000000000)

    @staticmethod
    def printResult(solution: Solution):
        string = ''
        for path in solution.paths:
            string += '0,'
            for e in path.edges():
                string += str(e) + ','
            string += '0,'
        string = string[:-1]
        print(f's {string}')
        print(f'q {solution.total_cost}')


class Utils:
    INF: float = math.inf

    @staticmethod
    def readOneStrPerLine(file: IO) -> str:
        return file.readline().split(':')[1].strip()

    @staticmethod
    def readOneIntPerLine(file: IO) -> int:
        return int(Utils.readOneStrPerLine(file))

    @staticmethod
    def getIntFromStr(string: str) -> int:
        return int(string.strip())

    @staticmethod
    def getWithDefault(val, default):
        return default if val is None else val

    @staticmethod
    def deepcopy(s):
        # TODO a better deep copy
        return copy.deepcopy(s)

    @staticmethod
    def randomDifferent2(length: int) -> Optional[Tuple[int, int]]:
        if length < 2:
            return None
        x1 = random.randint(0, length - 1)
        x2 = x1
        while x2 == x1:
            x2 = random.randint(0, length - 1)
        return x1, x2

    @staticmethod
    def getAscTuple2(pack: Tuple[int, int]):
        return pack if pack[0] <= pack[1] else (pack[1], pack[0])


def main():
    filename, time_limit, rnd_seed = sys.argv[1], sys.argv[3], sys.argv[5]
    random.seed(int(rnd_seed))
    graph_data = GraphData.extractData(filename)
    result = RunSolver.solve(graph_data, float(time_limit))
    RunSolver.printResult(result)


if __name__ == '__main__':
    t1 = time.time()
    main()
    print(f'Time consumed:{time.time() - t1}')

# CorrectnessTesting\verify.dat -t 6 -s 114
# sample.dat -t 6 -s 114
# CARP_samples\val1A.dat -t 6 -s 10

from ortools.linear_solver import pywraplp
from ortools.constraint_solver import pywrapcp, solver_parameters_pb2
from orm import lineup

class multi_solver():
    solver = {}  
    
    def __init__(self):
        self.solver = pywrapcp.Solver('FD', pywrapcp.Solver.DefaultSolverParameters()) 

    def solve(self, players, constraint_defs, proj_file_info, args):
        variables = []
        collector = self.solver.AllSolutionCollector()
        #collector = self.solver.LastSolutionCollector()
        lu_count = 10

        print('Running multi lineup solver...')
        #Define variables and constraints
        salary = 0
        roster_size = 0
        position_size = {}
        projected = 0
        for i, p in enumerate(players):
            var = self.solver.IntVar(0, 1, p.solver_id())
            salary += var * p.salary
            roster_size += var
            #Need to multiple by 100 so we are working with integers.
            projected += var * int(p.projected * 100)
            
            if not position_size.has_key(p.position):
                position_size[p.position] = 0
            position_size[p.position] += var

            variables.append(var)
            collector.Add(var)

        self.solver.Add(salary < 50000)
        self.solver.Add(roster_size == constraint_defs.num_of_players)
        for pos, min_limit, max_limit \
            in constraint_defs.pos_def:
                self.solver.Add(position_size[pos] >= min_limit)
                self.solver.Add(position_size[pos] <= max_limit)

        #Set object
        # ive expression
        score = 123 * 100
        obj_expr = self.solver.IntVar(score, score, "obj_expr")
        self.solver.Add(obj_expr <= projected)
        collector.AddObjective(obj_expr)
        
        #Create solution collector
        decision_builder = self.solver.Phase(variables, self.solver.CHOOSE_FIRST_UNBOUND, self.solver.ASSIGN_MIN_VALUE)
        
        print("Solving the problem sir...")
        #objective = self.solver.Maximize(obj_expr, 1)
        self.solver.Solve(decision_builder, collector)
        #self.solver.Solve(decision_builder, [objective,collector])
        num_of_solutions = collector.SolutionCount()
        print('Solutions found: {}'.format(num_of_solutions))

        if(num_of_solutions > 0):
            solution_index = num_of_solutions - 1 

            lups = []
            while (num_of_solutions - solution_index) <= lu_count:
                #print("SOLUTION INDEX:{}".format(solution_index))
                #print("Objective:{}".format(collector.ObjectiveValue(solution_index)))
                lu = lineup(proj_file_info[1],args.y,args.g,proj_file_info[0],0,constraint_defs.sort_func)
                
                for j, p in enumerate(players):
                    if(collector.Value(solution_index, variables[j]) == 1):
                        lu.players.append(p)
                
                lu.run_init_calc()
                lups.append(lu)
                solution_index -= 1        
            return lups
        
        return []
        


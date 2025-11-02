
from qiskit.transpiler import generate_preset_pass_manager  
from qiskit.transpiler.basepasses import TransformationPass


# create a class to have a custom pass 
class SimplifyAlternatingTripleCX(TransformationPass):
    """
    Custom pass: find pattern 
        CX(A,B), 
        CX(B,A), 
        CX(A,B) 
    and keep the middle CX(B,A) for optimization 
    """

    def run(self, dag):
        nodes = list(dag.topological_op_nodes())
        i = 0

        # Check 3 consecutive nodes at a time
        while i < len(nodes) - 2:
            n1, n2, n3 = nodes[i], nodes[i + 1], nodes[i + 2]

            # Make sure they are all cx gates 
            if n1.op.name == "cx" and n2.op.name == "cx" and n3.op.name == "cx":
                c1, t1 = n1.qargs
                c2, t2 = n2.qargs
                c3, t3 = n3.qargs

                # Find pattern CX(A,B), CX(B,A), CX(A,B) by checking target and control qubit of each CX gate 
                # Check that the middle CX gate is the "flipped" version of the one before and the one after 
                if c1 == c3 and t1 == t3 and c1 == t2 and t1 == c2:
                    # Remove the first and third CX gates
                    dag.remove_op_node(n1)
                    dag.remove_op_node(n3)

                    # Refresh node list since DAG changed
                    nodes = list(dag.topological_op_nodes())
                    
                    # Step back slightly to recheck surrounding gates (dont skip)
                    i = max(i - 1, 0)
                    continue

            # Continue the for loop 
            i += 1

        return dag


# add custom pass after optimization stage 
def createPassManager(backend):
    pm = generate_preset_pass_manager(
        optimization_level=3, backend=backend
    )
    pm.optimization += [SimplifyAlternatingTripleCX()]
    return pm

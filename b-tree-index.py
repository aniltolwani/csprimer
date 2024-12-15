# simple b-tree implementation
from typing import Union, Tuple

# make a type for B_plus_Tree_Node
B_plus_Tree_Node = object

class B_plus_Tree_Node(object):
    def __init__(self, min_nodes = 2, max_nodes = 4, is_leaf = True):
        self.children = []
        self.keys = []
        self.vals = []
        self.min_nodes = min_nodes
        self.max_nodes = max_nodes
        self.is_leaf = is_leaf
        


    def insert(self, key, value) -> Union[Tuple[B_plus_Tree_Node, B_plus_Tree_Node], B_plus_Tree_Node]:
        """
        Main B+Tree insert logic.
        
        1. Find the leaf node to insert into.
            a. Traverse using keys + children until we find the leaf node.
        2. Insert the key/value pair into the leaf node.
        3. Propagate the split up the tree.
        """

        # find a leaf type node, while keeping a call stack of parent calls in case we need to cascade splits
        if not self.is_leaf:
            k_idx = -1
            for i, k_node in enumerate(self.keys):
                if key < k_node:
                    k_idx = i
                    break
            n_idx = k_idx + 1 if k_idx != -1 else len(self.keys)
            ret = self.children[n_idx].insert(key, value)
            if isinstance(ret, tuple):
                # we can use an isinstance check for if a split occurred
                # importantly, this could be a leaf split or an internal split
                # but, we know the current node is an internal node, so we can safely use the result
                median_key, left_node = ret
                self.keys.insert(k_idx if k_idx != -1 else len(self.keys), median_key)
                self.children.insert(n_idx, left_node)
                if len(self.keys) > self.max_nodes:
                    median_key, left_node = self.split_internal()
                    # create a new root node
                    new_root = B_plus_Tree_Node(is_leaf=False)
                    new_root.keys = [median_key]
                    new_root.children = [left_node, self]
                    return new_root
                return self
            # if not, there was no split, just keep cascading the return up the callstack
            return ret
        
        # if we reach here, we're in a leaf node
        k_idx = -1
        for i, k_node in enumerate(self.keys):
            if key < k_node:
                k_idx = i
                break
        n_idx = k_idx + 1 if k_idx != -1 else len(self.keys)
        
        self.keys.insert(k_idx if k_idx != -1 else len(self.keys), key)
        self.vals.insert(n_idx, value)
        
        if len(self.keys) > self.max_nodes:
            median_key, left_node = self.split_leaf()
            # Check if we're root (no parent = no children list)
            if not self.children:  # Root leaf node
                new_root = B_plus_Tree_Node(is_leaf=False)
                new_root.keys = [median_key]
                new_root.children = [left_node, self]
                return new_root
            # Non-root leaf node - return split info to parent
            return median_key, left_node
        
        # if we reach here, we're done. just return the current node.
        return self


    def split_internal(self) -> Tuple[B_plus_Tree_Node, B_plus_Tree_Node]:
        """
        Split the node into two new nodes.
        """
        median_idx = len(self.keys) // 2
        median_value = self.keys[median_idx]
        
        # Create new left internal node
        left_node = B_plus_Tree_Node(is_leaf=False)
        left_node.keys = self.keys[:median_idx]  # Exclude median!
        left_node.children = self.children[:median_idx + 1]
        
        # Update old node (becomes right node)
        self.keys = self.keys[median_idx + 1:]
        self.children = self.children[median_idx + 1:]
        self.is_leaf = False
        return median_value, left_node

    def split_leaf(self) -> Tuple[int, B_plus_Tree_Node]:
        """
        Split the node into two new nodes.
        """
        # make the current node the right, and create a new left node   
        left = B_plus_Tree_Node()
        # for example if we have 5 keys, median will be index 2
        # so left slice should be 0, 1, and right slice should be 2, 3, 4
        median_idx = len(self.keys) // 2
        median_key = self.keys[median_idx]
        left.keys = self.keys[:median_idx]
        left.vals = self.vals[:median_idx]
        # preserve median in the current node
        self.keys = self.keys[median_idx:]
        self.vals = self.vals[median_idx:]
        return median_key, left 

    def pprint(self):
        """
        Pretty print the tree in a nice ascii-type format.
        Just to help us visualize as we make changes.
        """
        def _pprint(node, level=0):
            # Print current node's keys with proper indentation
            print('  ' * level + str(node.keys))
            
            # Recursively print children
            for child in node.children:
                _pprint(child, level + 1)
        
        # Start printing from root
        _pprint(self)

def __main__():
    root = B_plus_Tree_Node()
    print("Initial tree state:")
    root.pprint()
    # imagine these are (page_idx, row_idx pairs (i.e. in postgres))
    test_data = {
        "alice@gmail.com": (0, 0),
        "bob@gmail.com": (0, 1),
        "carol@gmail.com": (0, 2),
        "barb@gmail.com": (1, 0),
        "eve@gmail.com": (1, 1),
    }

    for email, (page_idx, row_idx) in test_data.items():
        root = root.insert(email, (page_idx, row_idx))
        print("Tree state after inserting test data:")
        root.pprint()

if __name__ == "__main__":
    __main__()

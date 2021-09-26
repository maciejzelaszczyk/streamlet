def ad_hoc_hash(epoch: int, nodes: int):
    '''Obviously, a garbage choice. Nevertheless, it does provide the randomness beneficial in debuging.'''
    return hash(str(epoch)) % nodes

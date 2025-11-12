class ModeloAnadirHost:
    def __init__(
        self,
        host: str = "",
        rw: bool = False,
        ro: bool = False,
        sync: bool = False,
        async_cb: bool = False,
        root_squash: bool = False,
        no_root_squash: bool = False,
        subtree_check: bool = False,
        no_subtree_check: bool = False,
        all_squash: bool = False,
        insecure: bool = False,
        secure: bool = False,
        anonuid: bool = False,
        anongid: bool = False
    ):
        self.host = host
        self.rw = rw
        self.ro = ro
        self.sync = sync
        self.async_cb = async_cb
        self.root_squash = root_squash
        self.no_root_squash = no_root_squash
        self.subtree_check = subtree_check
        self.no_subtree_check = no_subtree_check
        self.all_squash = all_squash
        self.insecure = insecure
        self.secure = secure
        self.anonuid = anonuid
        self.anongid = anongid

    def __repr__(self):
        return f"<ModeloAddHost host={self.host} opciones={{'rw': {self.rw}, 'ro': {self.ro}, 'sync': {self.sync}, 'async': {self.async_cb}, 'root_squash': {self.root_squash}, 'no_root_squash': {self.no_root_squash}, 'subtree_check': {self.subtree_check}, 'no_subtree_check': {self.no_subtree_check}, 'all_squash': {self.all_squash}, 'insecure': {self.insecure}, 'secure': {self.secure}, 'anonuid': {self.anonuid}, 'anongid': {self.anongid}}}>"

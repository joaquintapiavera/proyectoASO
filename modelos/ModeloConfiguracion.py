class ModeloConfiguracion:
    def __init__(self):
        self.iniciar_nfs = False
        self.nfsv4_habilitado = False
        self.gss_security = False
        self.dominio_nfsv4 = ""

    def set_iniciar_nfs(self, valor: bool):
        self.iniciar_nfs = valor

    def set_nfsv4(self, valor: bool):
        self.nfsv4_habilitado = valor

    def set_gss(self, valor: bool):
        self.gss_security = valor

    def set_dominio(self, dominio: str):
        self.dominio_nfsv4 = dominio.strip()

    def validar_configuracion(self):
        errores = []
        if self.nfsv4_habilitado and not self.dominio_nfsv4:
            errores.append("Debe ingresar un dominio NFSv4 si está habilitado NFSv4")
        return errores

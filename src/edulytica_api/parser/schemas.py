class __Schemas(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["wpc"] = "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
        self["cx"] = "http://schemas.microsoft.com/office/drawing/2014/chartex"
        self["cx1"] = "http://schemas.microsoft.com/office/drawing/2015/9/8/chartex"
        self["cx2"] = "http://schemas.microsoft.com/office/drawing/2015/10/21/chartex"
        self["cx3"] = "http://schemas.microsoft.com/office/drawing/2016/5/9/chartex"
        self["cx4"] = "http://schemas.microsoft.com/office/drawing/2016/5/10/chartex"
        self["cx5"] = "http://schemas.microsoft.com/office/drawing/2016/5/11/chartex"
        self["cx6"] = "http://schemas.microsoft.com/office/drawing/2016/5/12/chartex"
        self["cx7"] = "http://schemas.microsoft.com/office/drawing/2016/5/13/chartex"
        self["cx8"] = "http://schemas.microsoft.com/office/drawing/2016/5/14/chartex"
        self["mc"] = "http://schemas.openxmlformats.org/markup-compatibility/2006"
        self["aink"] = "http://schemas.microsoft.com/office/drawing/2016/ink"
        self["am3d"] = "http://schemas.microsoft.com/office/drawing/2017/model3d"
        self["o"] = "urn:schemas-microsoft-com:office:office"
        self["oel"] = "http://schemas.microsoft.com/office/2019/extlst"
        self["r"] = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        self["m"] = "http://schemas.openxmlformats.org/officeDocument/2006/math"
        self["v"] = "urn:schemas-microsoft-com:vml"
        self["wp14"] = "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
        self["wp"] = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
        self["w10"] = "urn:schemas-microsoft-com:office:word"
        self["w"] = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        self["w14"] = "http://schemas.microsoft.com/office/word/2010/wordml"
        self["w15"] = "http://schemas.microsoft.com/office/word/2012/wordml"
        self["w16cex"] = "http://schemas.microsoft.com/office/word/2018/wordml/cex"
        self["w16cid"] = "http://schemas.microsoft.com/office/word/2016/wordml/cid"
        self["w16"] = "http://schemas.microsoft.com/office/word/2018/wordml"
        self["w16sdtdh"] = "http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash"
        self["w16se"] = "http://schemas.microsoft.com/office/word/2015/wordml/symex"
        self["wpg"] = "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
        self["wpi"] = "http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
        self["wne"] = "http://schemas.microsoft.com/office/word/2006/wordml"
        self["wps"] = "http://schemas.microsoft.com/office/word/2010/wordprocessingShape"

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __getattr__(self, attr):
        return self[attr]

    @property
    def to_namespace(self):
        dict_return = {}
        for k, v in self.items():
            dict_return[k] = v
        return dict_return


schemas = __Schemas()

from typing import Optional, List


class Elem:
    """
    Class, that contains datas of structure element
    :param self.num: chapter number
    :param self.text: text attached to chapter
    :param self.sub_elements: subchapters of the chapter
    :param self.anchor_id: special id of the chapter
    """
    def __init__(self, num: str, text: str, anchor_id: str = None):
        self.num: str = num
        self.text: str = text
        self.sub_elements: Optional[List[Elem]] = None
        self.anchor_id: str = anchor_id

    def append(self, elem):
        """
        Appends a subchapter in self.sub_elements
        """
        if self.sub_elements is None:
            self.sub_elements = []
        self.sub_elements.append(elem)

    def __len__(self):
        """
        Returns the length of self.sub_elements
        """
        return 0 if self.sub_elements is None else len(self.sub_elements)

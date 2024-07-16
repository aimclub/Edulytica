from src.data_handling.VKRParser import ParserVKR

if __name__ == "__main__":
    """
    We will extract all VKRs in the specified range.
    """

    start_id = 723
    end_id = 15552

    parser = ParserVKR(start_id, end_id)
    parser.parse_vkrs()
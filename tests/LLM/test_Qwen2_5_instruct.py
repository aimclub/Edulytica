import unittest

from src.LLM.qwen.Qwen2_5_instruct import Qwen2_5_instruct, Qwen2_5_instruct_pipline


class TestQwen2_5_instruct(unittest.TestCase):
    def setUp(self):
        print("Start model setup")
        self.model = Qwen2_5_instruct()
        print("Model setup finish")

    def test_chat_template(self):
        system_p = ""
        user_p = ""
        cor_ans = [
            f'<|im_start|>system\n{system_p}<|im_end|>\n<|im_start|>user\n{user_p}<|im_end|>\n<|im_start|>assistant\n']
        self.assertEqual(cor_ans, self.model.apply_chat_template(system_p, [user_p]))

    def test_correct_generate_output_types(self):
        prompt = "Привет!"
        ans = self.model.generate([prompt])
        print(ans)
        self.assertIsInstance(ans, list)
        self.assertIsInstance(ans[0], str)


if __name__ == '__main__':
    unittest.main()

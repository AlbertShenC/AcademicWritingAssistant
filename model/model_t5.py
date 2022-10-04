# -*- coding: utf-8 -*-
__author__ = "Albert"
from fastT5 import OnnxT5, get_onnx_runtime_sessions
from transformers import T5Tokenizer


class ModelT5:
    def __init__(self, quantized=True, debug=False):
        self.quantized = quantized
        quantized_model_paths = ('./model/ckpt/encoder-quantized.onnx',
                                 './model/ckpt/decoder-quantized.onnx',
                                 './model/ckpt/init-decoder-quantized.onnx')
        model_paths = ('./model/ckpt/encoder.onnx',
                       './model/ckpt/decoder.onnx',
                       './model/ckpt/init-decoder.onnx')
        if debug:
            import os
            os.chdir('../')
        print('loading model...')

        self.tokenizer = T5Tokenizer.from_pretrained('t5-small', model_max_length=512)
        if quantized:
            model_sessions = get_onnx_runtime_sessions(quantized_model_paths)
        else:
            model_sessions = get_onnx_runtime_sessions(model_paths)
        self.model = OnnxT5('t5-small', model_sessions)

    def generate(self, input_str, return_num=10, beam_search_num=10):
        mask_token = '_'
        if mask_token not in input_str:
            return {'state': 'error',
                    'msg': 'No masked word is found!'}
        if return_num > beam_search_num:
            return {'state': 'error',
                    'msg': 'return_num is bigger than beam_search_num'}

        sentence = ''
        extra_id = 0
        for char in input_str:
            if not (char.isalpha() or char.isdigit()):
                if char == mask_token:
                    sentence += ' <extra_id_' + str(extra_id) + '> '
                    extra_id += 1
                else:
                    sentence += ' ' + char + ' '
            else:
                sentence += char
        if extra_id > 10:
            return {'state': 'error',
                    'msg': 'Too much masked words!'}

        token = self.tokenizer(sentence, return_tensors="pt")
        answers = self.model.generate(input_ids=token['input_ids'],
                                      attention_mask=token['attention_mask'],
                                      num_return_sequences=return_num,
                                      num_beams=beam_search_num)
        output = self.tokenizer.batch_decode(answers)

        print('generating...')
        result = []
        for single_output in output:
            result.append([])
            for idx in range(extra_id):
                start_extra_id = '<extra_id_' + str(idx) + '>'
                end_extra_id = '<extra_id_' + str(idx + 1) + '>'
                start_pos = single_output.find(start_extra_id) + len(start_extra_id)
                end_pos = single_output.find(end_extra_id)
                if start_pos == -1 or end_pos == -1 or start_pos >= end_pos:
                    result[-1].append('')
                else:
                    result[-1].append(single_output[start_pos:end_pos].strip())
        return {'state': 'success',
                'msg': result}


if __name__ == '__main__':
    model = ModelT5(quantized=False, debug=True)
    print(model.generate('_ experiments are conducted to verify the effectiveness and efficiency of the proposed method, which achieves state-of-the-art accuracies on popular benchmarks with a faster inference speed.'))
    print(model.generate('Extensive experiments are conducted to verify the effectiveness and efficiency of the proposed method, which achieves _ accuracies on popular benchmarks with a faster inference speed.'))

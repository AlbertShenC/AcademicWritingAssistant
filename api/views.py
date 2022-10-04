from django.http import HttpResponse, JsonResponse
from model.model_t5 import ModelT5


model = None
def index(request):
    return HttpResponse("You can test _ as you will.")


def check_model_state(request):
    global model

    if not model:
        return JsonResponse({'state': 'success',
                             'type': 'not loaded'})
    else:
        return JsonResponse({'state': 'success',
                             'type': 'quantized' if model.quantized else 'origin'})

def init_model(request):
    global model

    quantized = True if request.POST['quantized'] == 'true' else False
    if model:
        if model.quantized != quantized:
            del model
            model = ModelT5(quantized=quantized)
    else:
        model = ModelT5(quantized=quantized)

    return JsonResponse({'state': 'success',
                         'type': 'quantized' if quantized else 'origin'})


def generate(request):
    global model

    if not model:
        return JsonResponse({'state': 'error',
                             'msg': 'Model not inited!'})
    print(request.POST)
    if 'masked_input_str' not in request.POST:
        return JsonResponse({'state': 'error',
                             'msg': 'Empty request!'})
    masked_input_str = request.POST['masked_input_str']
    result = model.generate(masked_input_str)
    print(result)
    return JsonResponse(result)

import gradio as gr
def predict(image):
    return {'Food': 0.99}

if __name__ == '__main__':
    iface = gr.Interface(fn=predict, inputs='image', outputs='label')
    iface.launch()


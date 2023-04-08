class DataTile:
    def __init__(self, data, title, image=None):
        self.data = data
        self.title = title
        self.image = image

    @property
    def html(self):
        html = f'<div class="card"><h1>{self.title}</h1><p>{self.data}</p></div>'
        return html
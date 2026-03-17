class Stack():
    def __init__(self):
        self.list = []
    
    def pop(self):
        content = self.list.pop()
        return content
    
    def push(self, content):
        self.list.append(content)
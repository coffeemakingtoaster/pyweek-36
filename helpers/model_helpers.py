from os.path import join

# load_model will assume that the model is under
# /assets/models/<name>/<name>.obj
def load_model(name):
    model = loader.loadModel(join("assets","models",name, name+".obj"))
    #texture = loader.loadTexture("assets/models/"+name+"/"+name+".jpeg")
    #model.setTexture(texture)
    return model
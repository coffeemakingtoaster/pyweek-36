from direct.actor.Actor import Actor

class enemy_actor(Actor):
    
    def __init__(self):
        super().__init__("assets/anims/testanim2.bam",{"idle":"assets/anims/testanim2.bam"})
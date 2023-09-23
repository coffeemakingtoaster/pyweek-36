from entities.entity_base import enity_base
from config import GAME_CONSTANTS
from helpers.model_helpers import load_model
from panda3d.core import *
from config import MAP_CONSTANTS, ENTITY_TEAMS

from helpers.important_helpers import get_boss_name

from direct.actor.Actor import Actor
from entities.ranged_enemy import ranged_enemy
from entities.melee_enemy import melee_enemy
from entities.tank_enemy import tank_enemy
from entities.light_bullet import lightBullet_entity
from entities.bullet import bullet_entity

from direct.task.Task import Task

from os.path import join

import math
import time
import random


class BOSS_STATES:
    MELEE = "melee"
    RANGED = "ranged"


class boss(enity_base):
    def __init__(self, pos):
        super().__init__()

        self.name = get_boss_name()
        self.pos = pos
        self.model = Actor(
            "assets/anims/Boss.egg",
            {
                "Attack1": "assets/anims/Boss-Attack1.egg",
                "Sit": "assets/anims/Boss-Sit.egg",
                "Attack2": "assets/anims/Boss-Attack2.egg",
                "Attack3": "assets/anims/Boss-Attack4.egg",
                "Stand": "assets/anims/Boss-Stand.egg",
            },
        )
        self.model.setScale(2, 2, 2)
        self.model.setPos(pos)
        self.model.getChild(0).setP(90)
        self.model.getChild(0).setR(180)
        self.plnp = None

        self.speed = GAME_CONSTANTS.BOSS_MOVEMENT_SPEED

        self.id = "boss"

        self.team = ENTITY_TEAMS.ENEMIES

        self.notifier = CollisionHandlerEvent()
        self.notifier.addInPattern("%fn-into-%in")

        self.model.reparentTo(render)

        self.activationsphere = self.model.attach_new_node(CollisionNode("boss-sphere"))
        self.collision = self.model.attach_new_node(CollisionNode("boss"))

        self.activationsphere.setTag("team", ENTITY_TEAMS.ENEMIES)
        self.collision.setTag("team", ENTITY_TEAMS.ENEMIES)

        # Needed for preloading
        self.collision.setTag("id", self.id)
        self.activationsphere.node().setCollideMask(ENTITY_TEAMS.MELEE_ATTACK_BITMASK)
        self.collision.node().setCollideMask(ENTITY_TEAMS.ENEMIES_BITMASK)
        base.cTrav.addCollider(self.activationsphere, self.notifier)
        base.cTrav.addCollider(self.collision, self.notifier)
        min_point, max_point = self.model.getTightBounds()
        cp = CollisionSphere(0, 0, 0, 5)

        self.accept("bullet-into", self.bullet_hit)
        
        # Remove attack hitbox once the player has been damage 
        self.accept("player-got-hit", self._remove_hitbox)

        self.activationsphere.node().addSolid(cp)

        self.collision.node().addSolid(CollisionSphere(0, 0, 0, 1))
        #self.collision.show()
        base.cTrav.addCollider(self.activationsphere, CollisionHandlerEvent())

        self.current_hp = GAME_CONSTANTS.BOSS_HP

        self.active = False

        self.is_dead = False

        self.model.loop("Sit")

        self.state = BOSS_STATES.MELEE
        self.attackcooldown = GAME_CONSTANTS.BOSS_MELEE_ATTACK_COOLDOWN

        self.last_attack_time = max(
            GAME_CONSTANTS.BOSS_MELEE_ATTACK_COOLDOWN,
            GAME_CONSTANTS.BOSS_RANGED_ATTACK_COOLDOWN,
        )

        self.melee_attack_hitbox = None

        self.notifier = CollisionHandlerEvent()

        self.notifier.addInPattern("%fn-into-%in")

        self.bullets = []
        
        self.hit_sfx = base.loader.loadSfx(join("assets", "sfx", "enemy_hit.wav"))
        
        self.attack_1_sfx = base.loader.loadSfx(join("assets", "sfx", "boss_attack_1.wav"))
       
        self.attack_2_sfx = base.loader.loadSfx(join("assets", "sfx", "boss_attack_2.wav"))
        
        self.attack_3_sfx = base.loader.loadSfx(join("assets", "sfx", "boss_attack_3.wav"))
        
        self.shoot_sound = base.loader.loadSfx(join("assets", "sfx", "boss_shoot.wav"))

    # Set new  attack state/pattern
    def _roll_new_state(self):
        self.state = random.choice([BOSS_STATES.MELEE, BOSS_STATES.RANGED])
        if self.state == BOSS_STATES.MELEE:
            self.attackcooldown = GAME_CONSTANTS.BOSS_RANGED_ATTACK_COOLDOWN
        else:
            self.attackcooldown = GAME_CONSTANTS.BOSS_RANGED_ATTACK_COOLDOWN
        print("Now in {}".format(self.state))

    def update(self, dt, player_pos):
        entity_pos = self.model.getPos()

        delta_to_player = Vec3(
            entity_pos.x - player_pos.x, 0, entity_pos.z - player_pos.z
        )

        diff_to_player_normalized = Point2(
            delta_to_player.x, delta_to_player.z
        ).normalized()

        x = math.degrees(
            math.atan2(diff_to_player_normalized.x, diff_to_player_normalized.y)
        )

        x_direction = diff_to_player_normalized[0] * self.speed * dt
        z_direction = diff_to_player_normalized[1] * self.speed * dt

        if (delta_to_player.length() <= 2 and self.state == BOSS_STATES.MELEE) and (
            delta_to_player.length() <= 15 and self.state == BOSS_STATES.RANGED
        ):
            x_direction = 0
            z_direction = 0

        self.model.setX(self.model.getX() - x_direction)
        self.model.setZ(self.model.getZ() - z_direction)

        self.model.setR(x)

        if self.state == BOSS_STATES.MELEE:
            current_time = time.time()
            if (
                current_time - self.last_attack_time >= self.attackcooldown
                and delta_to_player.length() < 4
            ):
                self.attack()
                self.last_attack_time = current_time
        elif self.state == BOSS_STATES.RANGED:
            current_time = time.time()
            if current_time - self.last_attack_time >= self.attackcooldown:
                self.shoot(delta_to_player)
                self.last_attack_time = current_time

        # Safeguard
        if self.model.getY() > self.pos[1]:
            self.model.setY(self.pos[1])

        for i, bullet in enumerate(self.bullets):
            bullet.update(dt)
            if bullet.is_dead:
                bullet.destroy()
                del self.bullets[i]

    def shoot(self, delta_to_player):
        shoot_direction = delta_to_player.normalized() * -1
        quat = Quat()
        angle = 25 
        axis = Vec3(0, 1, 0).normalized()
        quat.setFromAxisAngle(-angle, axis)
        shoot_direction = quat.xform(shoot_direction) 
        self.shoot_sound.play()
        for i in range(3):
            quat = Quat()
            quat.setFromAxisAngle(angle, axis)
            shoot_direction = quat.xform(shoot_direction)
            self.bullets.append(
                lightBullet_entity(
                    self.model.getX(),
                    self.model.getZ(),
                    shoot_direction,
                    self.team,
                )
            )

    def _remove_hitbox(self, task=None):
        self.attack_1_sfx.stop()
        self.attack_2_sfx.stop()
        self.attack_3_sfx.stop()
        if self.melee_attack_hitbox is not None:
            self.melee_attack_hitbox.removeNode()
            self.melee_attack_hitbox = None
        else:
            Task.cont
        return Task.done

    def _activate_hitbox(self, task):
        if self.melee_attack_hitbox is not None:
            base.cTrav.addCollider(self.melee_attack_hitbox, self.notifier)
        return Task.done

    # This is only the melee attack
    def attack(self):
        attack_number = random.randint(1, 3)
        print("Attack {}".format(attack_number))
        # Cleanup. This covers an edge case that kept attack hitboxes to stay indefinelty
        if self.melee_attack_hitbox is not None:
            self._remove_hitbox(None)
        self.melee_attack_hitbox = self.model.attachNewNode(CollisionNode("attack"))
        #self.melee_attack_hitbox.show()
        attack_duration = 0
        wind_up_time = 0
        if attack_number == 1:
            self.model.play("Attack1")
            self.melee_attack_hitbox.node().addSolid(
                CollisionBox(Point3(0, 0, 0), 0.3, 1, 3)
            )
            self.melee_attack_hitbox.setPos(0.75, 0, -1)
            wind_up_time = 0.5
            attack_duration = 1.3
            self.attack_1_sfx.setLoop(True)
            self.attack_1_sfx.play()
        elif attack_number == 2:
            self.model.play("Attack2")
            self.melee_attack_hitbox.node().addSolid(
                CollisionBox(Point3(0, 0, 0), 2.75, 0.5, 2)
            )
            self.melee_attack_hitbox.setPos(0.1, 0, -1)
            wind_up_time = 0.5
            attack_duration = 1
            self.attack_2_sfx.setLoop(True)
            self.attack_2_sfx.play()
        else:
            self.model.play("Attack3")
            self.melee_attack_hitbox.node().addSolid(CollisionSphere(0, 0, 0, 4))
            self.melee_attack_hitbox.setPos(0, 0, 0)
            self.attack_3_sfx.setLoop(True)
            self.attack_3_sfx.play()
            wind_up_time = 0.5
            attack_duration = 1.1

        self.melee_attack_hitbox.setTag("team", ENTITY_TEAMS.PLAYER)
        # Set player team as player is the target
        self.melee_attack_hitbox.node().setCollideMask(
            ENTITY_TEAMS.MELEE_ATTACK_BITMASK
        )
        base.taskMgr.doMethodLater(
            wind_up_time, self._activate_hitbox, "destroy_boss_melee_attack_hitbox"
        )
        base.taskMgr.doMethodLater(
            attack_duration + wind_up_time,
            self._remove_hitbox,
            "destroy_boss_melee_attack_hitbox",
        )

    def _set_active(self, task):
        self.active = True
        return Task.done

    def activate(self):
        plight = PointLight("plight")
        plight.setColor((5, 5, 5, 5))
        self.plnp = self.model.attachNewNode(plight)
        self.plnp.setPos(0, 5, 0)
        plight.attenuation = (1, 0, 0.05)
        render.setLight(self.plnp)
        self.model.play("Stand")
        self.activationsphere.removeNode()
        # Wait for standup animation to finish
        base.taskMgr.doMethodLater(1, self._set_active, "activate_boss")
        base.musicManager.stopAllSounds()
        background_music = base.loader.loadMusic(join("assets", "music", "boss_music.mp3")) 
        background_music.setLoop(True)
        background_music.play()

    def take_damage(self, damage):
        if self.active:
            self.current_hp -= damage
            messenger.send("display_boss_hp", [self.current_hp])
            self.hit_sfx.play()
            if self.current_hp <= 0:
                self.is_dead = True
            # Every 5 damage => Possibly switch attack pattern
            if self.current_hp % 5 == 0:
                self._roll_new_state()

    # collisionentry is not needed -> we ignore it
    def bullet_hit(self, entry: CollisionEntry):
        # Ignore collisions triggered by other enemies
        if entry.into_node.getTag("id") != self.id:
            return

        # Only take damage from bullets targeted at own team
        if entry.into_node.getTag("team") != self.team:
            # print("nope")
            return

        self.take_damage(1)

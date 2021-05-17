from manimlib import *

#gravity
g = DOWN * 9

#colors
COLOR_MAP = ["#e62c29", "#ff312e", "#cc2725", "#ff4643", "#ff5a58", "#ff6f6d", "#ff8382", "#ff9897", "#ffadab"]

def get_heart():
    ## heart shape
    t = random.uniform(-1, 1)
    x = np.sin(t) * np.cos(t) * np.log(abs(t))
    y = np.sqrt(abs(t)) * np.cos(t)

    return np.array(
        [x, y, 0.0]
    )

def get_circular():
    t = random.uniform(0, TAU)
    r = random.uniform(0.4, 1.0)
    x = r * np.cos(t)
    y = r * np.sin(t)
    return np.array(
        [x, y, 0.0]
    )

class Particle(VGroup):
    CONFIG = {
        "size" : 0.05,
        "color" : BLUE,
        "shape" : get_circular
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time = 0.0
        self.velocity = self.shape() * 8
        self.explode = False
        self.done = False
        self.add_body()
        self.anims = []
        self.add_updater(lambda m, dt: m.update_time(dt))
        self.add_updater(lambda m : m.progress_through_anims())
        self.add_updater(lambda m, dt : m.explosion(dt))


    def add_body(self):
        body = Dot().set_color(self.color).set_height(self.size)
        body.move_to(self.get_center())
        self.body = body
        self.add(self.body)

    def update_time(self, dt):
        self.time += dt

    def explosion(self, dt):
        if self.explode:
            self.velocity += g * dt
            self.shift(self.velocity * dt)
            self.velocity *= 0.95
            self.body.set_opacity(self.body.get_opacity() * 0.95)
            self.body.set_height(self.body.get_height() * 0.95)

            if self.body.get_opacity() < EPSILON:
                self.done = True

    def push_anim(self, anim):
        anim.suspend_mobject_updating = False
        anim.begin()
        anim.start_time = self.time
        self.anims.append(anim)

    def pop_anim(self, anim):
        anim.update(1)
        anim.finish()
        self.burst()
        self.anims.remove(anim)

    def progress_through_anims(self):
        for anim in self.anims:
            alpha = (self.time - anim.start_time) / anim.run_time
            anim.interpolate(alpha)
            if alpha >= 1.0:
                self.pop_anim(anim)

    def burst(self):
        self.explode = True

class Cracker(VGroup):
    CONFIG = {
        "color" : BLUE,
        "n_particles" : 100,
        "shape" : get_circular
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_particles()

    def create_particles(self):
        cracker = VGroup()
        for _ in range(self.n_particles):
            p = Particle(color=self.color, shape=self.shape)
            cracker.add(p)
        self.cracker = cracker
        self.add(self.cracker)

    def done(self):
        result = True
        for p in self.cracker:
            if p.done:
                result *= True
            else:
                result *= False
        return result

    def set_burst_height(self, h, run_time=1.0):

        def moving(m, alpha):
            m.restore()
            m.shift(UP * h * alpha)
        for p in self.cracker:
            p.save_state()
            anim = UpdateFromAlphaFunc(
            p,
            moving, run_time=run_time
            )
            p.push_anim(anim)





class Firework(VGroup):
    CONFIG = {
        "frequency" : 0.1,
        "colors" : [BLUE, GREEN, RED, PINK, ORANGE, TEAL],
        "n_cracker_particles" : 100,
        "shape" : get_circular
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.create_crackers()
        self.running = True
        self.add_updater(lambda m, dt : m.start_firwork(dt))
        self.add_updater(lambda m, dt : m.clear_the_clutter(dt))

    def create_crackers(self):
        self.crackers = VGroup()
        self.add(self.crackers)

    def make_a_cracker(self, pos):
        col = random.choice(self.colors)
        cracker = Cracker(color=col, shape=self.shape).shift(pos)
        return cracker

    def clear_the_clutter(self, dt):
        for c in self.crackers:
            if c.done():
                self.crackers.remove(c)

    def start_firwork(self, dt):
        if random.random() < self.frequency and self.running:
            d_to_sky = random.uniform(4, FRAME_HEIGHT-1)
            cracker = self.make_a_cracker(DOWN * (FRAME_Y_RADIUS + 1) + random.uniform(-FRAME_X_RADIUS, FRAME_X_RADIUS) * RIGHT)
            cracker.set_burst_height(d_to_sky)
            self.crackers.add(cracker)

    def stop_firework(self):
        self.running = False

class Test(Scene):
    def construct(self):
        f = Firework(colors = COLOR_MAP)
        self.add(f)

        self.wait(3)
        f.stop_firework()
        self.wait(2)

        c = Cracker(color=BLUE).shift(DOWN * 8)
        c.set_burst_height(7)
        self.add(c)
        self.wait(3)

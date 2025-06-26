import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

class Conway:
    def __init__(self, size, lattice = None):
        self.rng = np.random.default_rng()
        self.size = size

        # initialises the lattice based on whether one is provided or not, if it isn't a random lattice is initialised
        # 1 represents alive, 0 represents dead
        if lattice is None:
            self.lattice = self.rng.integers(0, 1, size = (self.size, self.size), endpoint = True)
        else:
            if lattice.shape == (self.size, self.size):
                self.lattice = lattice
            else:
                raise Exception("Lattice given does not match the size")

    def step_gol(self):
        # arbitrary names, dont necessarily mean its correct
        up = np.roll(self.lattice, 1, axis = 0)
        down = np.roll(self.lattice, -1, axis = 0)
        right = np.roll(self.lattice, 1, axis = 1)
        left = np.roll(self.lattice, -1, axis = 1)
        upright = np.roll(up, 1, axis = 1)
        upleft = np.roll(up, -1, axis = 1)
        downright = np.roll(down, 1, axis = 1)
        downleft = np.roll(down, -1, axis = 1)

        living = up + down + right + left + upright + upleft + downright + downleft

        alive = self.lattice == 1
        dead = self.lattice == 0

        mask1 = living < 2
        mask2 = living > 3
        mask3 = living == 3

        # runs update rules
        self.lattice[alive*mask1] = 0
        self.lattice[alive*mask2] = 0
        self.lattice[dead*mask3] = 1

    def game_of_life(self, fps):
        fig = plt.figure(figsize = (10, 10))
        im = plt.imshow(self.lattice, interpolation = "none", aspect = "auto", vmin = -0.25, vmax = 1, cmap = "Greys_r")
        plt.title("Conway's Game of Life")

        def animate(i):
            self.step_gol()
            print(np.sum(self.lattice))
            im.set_array(self.lattice)
            return [im]

        anim = animation.FuncAnimation(fig, animate, interval = 1000/fps, blit = True)
        plt.show()

    def measurement(self):
        active = []
        times = []
        for i in range(1000):
            # resets the lattice to a randomized one
            self.lattice = self.rng.integers(0, 1, size = (self.size, self.size), endpoint = True)

            # holds number of active cells, active being the number of alive cells
            # initialized so that the while loop works properly
            # tracks 20 latest ones only, if all 20  are equal to each other, then the game is considered to be in equilibrium
            tracker = list(range(20))

            # if there is oscillation, sets will be a list of the periods of said oscillation.
            # this will be tracked for the past 20 updates
            sets = list(range(20))

            t = 0

            # runs game of life until equilibrium
            # very important is that sometimes the game might oscillate between multiple states, so we track the period of oscillation.
            # I assume that higher periods of oscillation are much more unlikely so, I dont consider any state where the period could be larger than 4
            while len(set(sets)) != 1 or sets[-1] > 4:
                t += 1
                self.step_gol()
                tracker.append(int(np.sum(self.lattice)))
                tracker.pop(0)

                # appends period of oscillation
                sets.append(len(set(tracker)))
                sets.pop(0)

            # for curiosity, saves any state with an oscillation of active sites of more than 2
            if sets[-1] > 2:
                np.savetxt("Blinker" + str(set(tracker)) + ".csv", self.lattice, delimiter = ",")

            # store the active cells at equilibrium
            times.append(t-20)
            active.append(np.average(tracker))
            print("Measurement Number: " + str(i))
            print(tracker)
        active = np.array(active)
        times = np.array(times)
        np.savetxt("ConwayActive.csv", active, delimiter = ",")
        np.savetxt("ConwayTimes.csv", times, delimiter=",")



def cm_glider(size, glider):
    g = np.array(([0, 1, 0], [0, 0, 1], [1, 1, 1]))
    glider = np.zeros((size, size))
    glider[int(size / 2) - 1:int(size / 2) + 2, int(size / 2) - 1:int(size / 2) + 2] = g
    game_of_life = Conway(size, glider)

    center_mass = []

    for _ in range(10001):

        vectors = []
        for i in range(size):
            for j in range(size):
                if game_of_life.lattice[i, j] == 1:
                    vectors.append([i, j])
        vectors = np.array(vectors)

        # Calculates the center of mass
        up = np.min(vectors[:, 0])
        down = np.max(vectors[:, 0])
        left = np.min(vectors[:, 1])
        right = np.max(vectors[:, 1])

        # if crossing boundary makes sure cm is calculated properly
        if down-up == size-1:
            for i in range(len(vectors)):
                if vectors[i, 0] > int(size/2):
                    vectors[i, 0] -= size

        if right-left == size-1:
            for i in range(len(vectors)):
                if vectors[i, 1] > int(size / 2):
                    vectors[i, 1] -= size

        cm = np.mean(vectors, axis = 0)

        # if cm falls outside of lattice, repositions it inside of it
        if cm[0] < 0:
            cm[0] = size + cm[0]
        if cm[1] < 0:
            cm[1] = size + cm[1]

        center_mass.append(cm)
        game_of_life.step_gol()

    center_mass = np.array(center_mass)
    print(center_mass)
    displacement = np.zeros((len(center_mass)-1, 2))

    # calculates the displacement while also accounting for boundaries
    for i in range(len(displacement)):
        diff = center_mass[i+1] - center_mass[i]
        if np.abs(diff[0]) > int(size/2):
            diff[0] -= size
        elif np.abs(diff[1]) > int(size/2):
            diff[1] -= size
        displacement[i] = diff
    print(displacement)

    speed = np.average(displacement, axis=0)
    print("Velocity:", speed)
    print("Speed:", np.linalg.norm(speed))
    print("This would be correct in a continuous space, but the game of life runs on a discrete lattice. This means the "
          "norm of the velocity isn't actually the speed of the glider.")
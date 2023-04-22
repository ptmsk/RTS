import numpy as np
from timeit import default_timer as timer
from utils import *

class RTS:
    def __init__(self):
        self.init_param()


    def init_param(self):
        self.rtable = [0]
        self.next = [-1]
        self.tail = [0]
        self.run_s = []
        self.run_e = []
        self.run = []


    @measure_time
    def run_ccl(self, img):
        M, N = img.shape
        p = img.flatten()
        l = 1

        i = 0
        while i < N*M:
            if p[i]:
                j = 0
                self.run_s.append(i)
                i += 1
                if i % N:
                    while p[i]:
                        i += 1
                        if i % N == 0:
                            break
                self.run_e.append(i - 1)

                run_s_ab = self.run_s[-1] - N - 1 if self.run_s[-1] % N else self.run_s[-1] - N
                while self.run_e[j] < run_s_ab:
                    j += 1
                if self.run_e[j] <= self.run_e[-1] - N:
                    self.run.append(self.run[j])
                    j += 1

                    while self.run_e[j] <= self.run_e[-1] - N:
                        self.resolve(self.rtable[self.run[j]], self.rtable[self.run[-1]])
                        j += 1
                    
                    if (self.run_e[-1] + 1) % N:
                        if self.run_s[j] <= self.run_e[-1] - N + 1:
                            self.resolve(self.rtable[self.run[j]], self.rtable[self.run[-1]])
                    else:
                        if self.run_s[j] <= self.run_e[-1] - N:
                            self.resolve(self.rtable[self.run[j]], self.rtable[self.run[-1]])

                    # Update object pixel to provisional label
                    p[self.run_s[-1]:self.run_e[-1]+1] = self.run[-1]

                    # Discard unnecessary run
                    discard_end = j + 1
                    if self.run_e[j] > self.run_e[-1] - N:
                        discard_end = j
                    
                    del self.run[:discard_end], self.run_s[:discard_end], self.run_e[:discard_end]
                elif (self.run_s[j] <= self.run_e[-1] - N + 1 and (self.run_e[-1] + 1) % N) or (self.run_s[j] <= self.run_e[-1] - N and (self.run_e[-1] + 1) % N == 0):
                    self.run.append(self.run[j])

                    # Update object pixel to provisional label
                    p[self.run_s[-1]:self.run_e[-1]+1] = self.run[-1]

                    # Discard unnecessary run
                    discard_end = j + 1
                    if self.run_e[j] > self.run_e[-1] - N:
                        discard_end = j
                    
                    del self.run[:discard_end], self.run_s[:discard_end], self.run_e[:discard_end]
                else:
                    self.run.append(l)
                    self.rtable.append(l)
                    self.next.append(-1)
                    self.tail.append(l)

                    # Update object pixel to provisional label
                    p[self.run_s[-1]:self.run_e[-1]+1] = self.run[-1]

                    l += 1
            else:
                i += 1

        # Second scan
        for i in range(M*N):
            """
            if p[i]:
                p[i] = self.rtable[p[i]]
            """
            # Save 0 as representative label for background pixel for simplicity
            p[i] = self.rtable[p[i]]

        return p.reshape((M, N))
    
    def vis_run_ccl(self, img, dest_path):
        M, N = img.shape
        p = img.flatten()
        p[p == 1] = -1
        l = 1

        i = 0
        idx = 0

        color_code = {}
        mask_color = (192, 192, 192)
        assign_color_code(color_code, 0)
        assign_color_code(color_code, -1)

        res_flat = np.zeros((M*N, 3), dtype=int)
        out_image = res_flat.reshape((M, N, 3))

        for label in color_code:
            res_flat[p == label] = color_code[label]

        idx = save_image(out_image, dest_path, idx)

        begin_time = timer()

        while i < N*M:
            if p[i]:
                j = 0
                self.run_s.append(i)
                idx = apply_color(out_image, i//N, i%N, mask_color, dest_path, idx)
                i += 1
                if i % N:
                    if p[i]:
                        idx = apply_color(out_image, i//N, i%N, mask_color, dest_path, idx)
                    while p[i]:
                        i += 1
                        if i % N == 0:
                            break
                        if p[i]:
                            idx = apply_color(out_image, i//N, i%N, mask_color, dest_path, idx)
                self.run_e.append(i - 1)

                run_s_ab = self.run_s[-1] - N - 1 if self.run_s[-1] % N else self.run_s[-1] - N
                while self.run_e[j] < run_s_ab:
                    j += 1
                if self.run_e[j] <= self.run_e[-1] - N:
                    self.run.append(self.run[j])
                    p[self.run_s[-1]:self.run_e[-1]+1] = self.run[-1]

                    for label in color_code:
                        if label in [0, -1]:
                            continue
                        res_flat[p == label] = color_code[label]

                    idx = save_image(out_image, dest_path, idx)

                    j += 1

                    while self.run_e[j] <= self.run_e[-1] - N:
                        self.resolve(self.rtable[self.run[j]], self.rtable[self.run[-1]])
                        j += 1
                    
                    if (self.run_s[j] <= self.run_e[-1] - N + 1 and (self.run_e[-1] + 1) % N) or (self.run_s[j] <= self.run_e[-1] - N and (self.run_e[-1] + 1) % N == 0):
                        self.resolve(self.rtable[self.run[j]], self.rtable[self.run[-1]])

                    # Update object pixel to provisional label
                    p[self.run_s[-1]:self.run_e[-1]+1] = self.run[-1]

                    # Discard unnecessary run
                    discard_end = j + 1
                    if self.run_e[j] > self.run_e[-1] - N:
                        discard_end = j
                    
                    del self.run[:discard_end], self.run_s[:discard_end], self.run_e[:discard_end]
                    
                elif (self.run_s[j] <= self.run_e[-1] - N + 1 and (self.run_e[-1] + 1) % N) or (self.run_s[j] <= self.run_e[-1] - N and (self.run_e[-1] + 1) % N == 0):
                    self.run.append(self.run[j])
                    p[self.run_s[-1]:self.run_e[-1]+1] = self.run[-1]

                    for label in color_code:
                        if label in [0, -1]:
                            continue
                        res_flat[p == label] = color_code[label]

                    idx = save_image(out_image, dest_path, idx)

                    # Update object pixel to provisional label
                    p[self.run_s[-1]:self.run_e[-1]+1] = self.run[-1]

                    # Discard unnecessary run
                    discard_end = j + 1
                    if self.run_e[j] > self.run_e[-1] - N:
                        discard_end = j
                    
                    del self.run[:discard_end], self.run_s[:discard_end], self.run_e[:discard_end]
                else:
                    self.run.append(l)
                    self.rtable.append(l)
                    self.next.append(-1)
                    self.tail.append(l)
                    assign_color_code(color_code, l)

                    # Update object pixel to provisional label
                    p[self.run_s[-1]:self.run_e[-1]+1] = l
                    
                    for label in color_code:
                        res_flat[p == label] = color_code[label]

                    idx = save_image(out_image, dest_path, idx)


                    l += 1

            else:
                res_flat[i] = mask_color

                idx = save_image(out_image, dest_path, idx)

                res_flat[i] = color_code[0]
        
                i += 1

        # Second scan
        for i in range(M*N):
            """
            if p[i]:
                p[i] = self.rtable[p[i]]
            """
            # Save 0 as representative label for background pixel for simplicity
            if p[i]:
                res_flat[i] = mask_color

                idx = save_image(out_image, dest_path, idx)

                p2r = p[i] != self.rtable[p[i]]

                p[i] = self.rtable[p[i]]

                res_flat[i] = color_code[p[i]]

                if p2r:
                    idx = save_image(out_image, dest_path, idx)
            else:
                res_flat[i] = mask_color

                idx = save_image(out_image, dest_path, idx)

                res_flat[i] = color_code[0]
        
        end_time = timer()

        return p.reshape((M, N)), end_time - begin_time


    def resolve(self, x, y):
        """
        Resolve the label equivalences between provisional label sets
        """

        u = self.rtable[x]
        v = self.rtable[y]

        if u < v:
            self.merge_operation(u, v)
        elif u > v:
            self.merge_operation(v, u)

    def merge_operation(self, u, v):
        """
        Connect two provisional label sets
        """
        i = v
        while i != -1:
            self.rtable[i] = u
            i = self.next[i]

        self.next[self.tail[u]] = v
        self.tail[u] = self.tail[v]


if __name__ == "__main__":
    print("--RTS Algorithm--")

    np.random.seed(42)
    img = np.random.randint(2, size=(10, 20))
    # img = np.random.randint(2, size=(10, 10))

    rts = RTS()

    p, _ = rts.vis_run_ccl(img, "vis")

    # print(img, '\n')

    print(p, '\n')
    print(rts.run)
    print(rts.rtable)
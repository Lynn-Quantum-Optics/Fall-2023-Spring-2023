# file to try out Lynn's idea of symmetrized bell states

import numpy as np
from functools import partial
from u_parametrize import *
from trabbit import trabbit


def check_entangled(bell, ret_val = False, display_val=False):
    '''Computes reduced density matrix for each particle and checks if they are mixed.

    Note: performs the partial trace over the second subsystem.

    :bell: d^2 x 1 vector
    :ret_val: boolean to return the trace of rdm squared
    :display_val: boolean to display the reduced density matrix and the trace of the rdm squared
    
    '''
    # get d from the bell state and make sure it's normalized
    d = int(np.sqrt(len(bell)))
    bell = bell.reshape((d**2))
    bell /= np.linalg.norm(bell)

    # get density matrix
    rho = np.outer(bell, np.conj(bell))

    # get reduced density matrix
    rho_reduced = np.zeros((d, d), dtype=complex)

    # partial trace over the second subsystem
    for i in range(d):
        # projector for each basis state of the second subsystem
        basis_state = np.zeros(d)
        basis_state[i] = 1
        projector = np.kron(basis_state, np.eye(d))

        # add to reduced density matrix
        rho_reduced += np.dot(np.dot(projector, rho), projector.T)

    # normalize!
    rho_reduced = np.trace(rho_reduced) * rho_reduced
    
    # expect 1/d for fully entangled system
    tr_sq =  np.trace(rho_reduced @ rho_reduced)
    if display_val:
        # print(rho_reduced)
        print(tr_sq)
    if ret_val:
        return tr_sq
    return np.isclose(tr_sq, 1/d, 1e-10)

def bell_us(d, c, p):
    '''Function to generate a bell state in the joint particle basis in the old way.

    Params:
        :d: dimension of the system
        :c: correlation class
        :p: phase class
    
    '''
    bell = np.zeros((d**2, 1), dtype=complex)
    for j in range(d):
        L = j
        R = (j+c) % d
        index = L*d + R
        bell[index] = np.exp(2*np.pi*1j*p*j / d)

    # normalize
    bell /= np.sqrt(d)

    return bell

def bell_s_2(d, c, p):
    '''Function to generate a bell state in the joint particle basis that specifically is symmetric.

    Params:
        :d: dimension of the system
        :c: correlation class
        :p: phase class
    
    '''
    bell = np.zeros((d**2, 1), dtype=complex)
    for j in range(d):
        # only mess with terms for c!= 0 or d/2
        if c == 0 or (d % 2 == 0 and j == d//2):
            L = j
            R = (j+c) % d
            index = L*d + R
            bell[index] = np.exp(2*np.pi*1j*p*j / d)
        else:
            # use the c = 1, p = 0 bell state as basis to tweak
            effective_c = 1
            # effective_p = 0
            L = j
            R = (j+effective_c) % d
            index = L*d + R
            index_swap = R*d + L
            if c < d//2: # keep symmetrized; minus sign goes where j is 
                # p tells us where to put minus sign
                if j == p: # put minus here
                    bell[index] = -1
                    bell[index_swap] = -1
                else:
                    bell[index] = 1
                    bell[index_swap] = 1
            else: # anti-symmetrize
                # print(p, j)
                if j == p: # put minus here
                    bell[index] = -1
                    bell[index_swap] = 1
                else:
                    bell[index] = 1
                    bell[index_swap] = -1
    # print('-----')
    # print(f'c = {c}, p = {p}, bell = {display_bell(np.round(bell, 10))}')     
    # normalize
    bell /= np.linalg.norm(bell)
    return bell

def bell_s(d, c, p):
    '''Function to generate a bell state in the joint particle basis that specifically is symmetric.

    Params:
        :d: dimension of the system
        :c: correlation class
        :p: phase class
    
    '''
    bell = np.zeros((d**2, 1), dtype=complex)
    for j in range(d):
        L = j
        R = (j+c) % d
        index = L*d + R
        bell[index] = np.exp(2*np.pi*1j*p*j / d)
        if c!= 0 or (d % 2 == 0 and j == d//2):
            index = R*d + L
            bell[index] = np.exp(2*np.pi*1j*p*j / d)
            if p %2 == 0: # if even p
                bell[0] = np.exp(2*np.pi*1j*p*j / d)

    # normalize
    bell /= np.linalg.norm(bell)
    return bell

def symmetric(bell=None, ret_norm=False, display=False):
    '''Checks if an input bell state (in joint particle basis) is symmetric wrt particle exchange.

    Params:
        :bell: d^2 x 1 vector
        :ret_norm: boolean to return the norm of the bell state - new bell
        :display: boolean to display initial and transformed

    Note: by construction, the L state corresponds to the index // d, R is index % d. Thus, index = L*d + R
    '''
    d = int(np.sqrt(len(bell)))
    bell = bell.reshape((d**2, 1))
    bell /= np.linalg.norm(bell)

    # need to swap L and R and check if they are the same
    new_bell = np.zeros((d**2,1), dtype=complex)
    for i, b in enumerate(bell):
        if b != 0:
            L = i // d
            R = i % d
            new_i = int(R*d + L)
            new_bell[new_i] = b
    
    # account for overall phase
    # find phase of first nonzero term
    first_non0 = bell[np.nonzero(bell)[0][0]]
    imag_orig = np.imag(first_non0)
    phase_orig = np.angle(first_non0)
    phase_new = np.angle(new_bell[np.nonzero(new_bell)[0][0]])

    if phase_orig != phase_new and np.isclose(imag_orig, 0, 1e-10):
        new_bell *= np.exp(1j*(phase_orig - phase_new))

    if display:
        print(bell)
        print('------')
        print(new_bell)

    if ret_norm:
        return np.linalg.norm(bell - new_bell)

    return np.all(np.isclose(bell, new_bell, 1e-10))

def find_cp(d, bell_func = bell_us, operation=symmetric):
    '''Finds what c and p for given d will yield symmetric state'''
    valid_cp = []
    for c in range(d):
        for p in range(d):
            if operation(bell_func(d, c, p)):
                valid_cp.append((c, p))

    print(f'Num valid c, p: {len(valid_cp)}')
    return valid_cp
        
def check_all_bell(d, func = None, bell_gen_func = bell_us):
    '''Performs the function func on each of the bell states for a given dimension d.

    Params:
        :d: dimension of the system
        :func: function to perform on each bell state. default is None, which just prints the bell states without doing anything
        :bell_gen_func: function to generate the bell states. default is bell_us, which generates the bell states in the old way
    '''

    for c in range(d):
        for p in range(d):
            print(c, p)
            if func is not None:
                print(func(bell_gen_func(d, c, p)))
            else:
                print(bell_gen_func(d, c, p), display_val=True)
            print('-----')

def check_all_entangled(d, bell_gen_func = bell_s):
    '''Performs the function func on each of the bell states for a given dimension d.

    Params:
        :d: dimension of the system
        :func: function to perform on each bell state. default is None, which just prints the bell states without doing anything
        :bell_gen_func: function to generate the bell states. default is bell_us, which generates the bell states in the old way
    '''
    entangled = 0

    for c in range(d):
        for p in range(d):
            print(c, p)
            ent = check_entangled(bell_gen_func(d, c, p), display_val=True)
            if ent == True:
                entangled += 1
            print('-----')

    return entangled

def display_bell(bell):
    '''Converts bell state as vector and prints it in bra ket form.'''
    d = int(np.sqrt(len(bell)))
    bell = bell.reshape((d**2, 1))
    bell /= np.linalg.norm(bell)
    bell_str = ''
    for i, b in enumerate(bell):
        if b != 0:
            L = i // d
            R = i % d
            if bell_str == '':
                bell_str+=f'{np.round(b[0],3)} |{L}>|{R}>'
            else:
                bell_str+=f'+ {np.round(b[0],3)} |{L}>|{R}>'
    return bell_str

def make_entangled(bell):
    '''Uses GD to find the state we need to add to the bell state to make it fully entangled'''
    d = int(np.sqrt(len(bell)))
    bell = bell.reshape((d**2,))
    bell /= np.linalg.norm(bell)

    entanglement = partial(check_entangled, ret_val=True)
    symmet = partial(symmetric, ret_norm=True)

    def loss(x, bell):
        # convert to full vector
        vec = x[:d**2] + 1j*x[d**2:]
        bell += vec
        ent = entanglement(bell)
        sym = symmet(bell)
        ent_real = np.real(ent)
        ent_imag = np.imag(ent)
        targ_ent = 1/d
        return (ent_real - targ_ent)**2 + (ent_imag)**2 + sym**2
    
    def random_gen():
        '''Separate real and imaginary parts of vector and normalize'''
        vec = np.concatenate([np.random.rand(d**2), + 1j*np.random.rand(d**2)])
        combined_vec = vec[:d**2] + 1j*vec[d**2:]
        return vec/np.linalg.norm(combined_vec)
    
    # try to find solution
    loss_bell = partial(loss, bell=bell)
    x_best, loss_best = trabbit(loss_bell, random_gen, verbose=True, frac=0.01, alpha=1.1, tol=1e-10)
    print(loss_best)
    print(x_best)
    return x_best


if __name__ == '__main__':
    d = 4

    bell = bell_s(d, 3, 2)
    x_best = make_entangled(bell)

    # found one to 1e-6!
#     1.439455219012125e-06
# [ 1.33466454+0.j          0.07991565+0.j          1.02935334+0.j
#   0.0366273 +0.j          0.05358747+0.j          1.49809086+0.j
#   0.41675159+0.j          0.13737118+0.j          1.00378665+0.j
#   0.413834  +0.j         -1.13016502+0.j          1.12790242+0.j
#   0.04500242+0.j          0.1557045 +0.j          1.15604772+0.j
#   0.88953439+0.j          0.13977298+0.56855612j  0.04592478+0.35555318j
#   0.03116871+0.36767168j  0.02682425+0.32866123j  0.04411716+0.84818717j
#   0.03743956+0.5903136j   0.03449962+0.82848295j  0.03551454+0.09278652j
#   0.03277864+0.52779357j  0.03484632+0.4725063j   0.03543179+0.3985269j
#   0.03604953+0.68849192j  0.02781067+0.32030142j  0.03556816+0.36482586j
#   0.03580318+0.58050521j  0.03926356+0.7201627j ]

#     x_best =  np.array([
#     -0.39914514+0.j, 0.66802457+0.j, 0.37203545+0.j, -0.04055752+0.j, 
#     0.16172204+0.j, -0.25811277+0.j, 0.59908882+0.j, -0.31932903+0.j, 
#     -0.0760946 +0.j, -0.37229527+0.j, 0.40606246+0.j, 0.65354633+0.j, 
#     0.68968878+0.j, 0.2965142 +0.j, 0.08393382+0.j, 0.16422431+0.j, 
#     -0.03314695+0.21097571j, -0.00292451+0.03471294j, -0.02812834+0.34831972j, 
#     -0.02904904+0.53232796j, -0.02018416+0.15073022j, -0.03323988+0.31055887j, 
#     -0.02743774+0.55702722j, -0.03312472+0.05832004j, -0.04125797+0.07318349j, 
#     -0.03802235+0.56537948j, -0.05016439+0.37928723j, -0.04993331+0.42466573j, 
#     -0.0270885 +0.10596727j, -0.06731255+0.27162313j, -0.06944027+0.47743037j, 
#     -0.05154533+0.3501594j
# ]) # loss = 3.48e-07; not symmetric
    
    corr = x_best[:d**2]+1j*x_best[d**2:]
    corr = corr.reshape((d**2, 1))
    print('correction', display_bell(corr))
    bell_corr = bell + corr
    print('is symmetric?', symmetric(bell_corr, display=True))


    # print(check_entangled(bell_s(d, 3, 2), display_val=True))
    # print(display_bell(bell_s(d, 3, 2)))



    # print('Symmetrizing')
    # print(find_cp(d, bell_s, check_entangled))
    # print(find_cp(d, bell_s, symmetric))
    # print('-----')
    # print('Us')
    # print(find_cp(d, bell_us, check_entangled))
    # print(find_cp(d, bell_us, symmetric))
    # check_all_bell(d, display_bell, bell_s)
    # print(check_all_entangled(d))
    # find_params(d, bell_s)
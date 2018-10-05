import numpy as np
import matplotlib.pyplot as plt

fi = open("./data", "r")

data = [float(x) for x in fi.readlines()]

#np.histogram(data, 10)
weights = 100.*np.ones_like(data)/float(len(data))
plt.hist(data, weights = weights, bins=[-0.025, -0.020, -0.015, -0.010, -0.005, 0., 0.005, 0.010, 0.015, 0.020, 0.025])
#plt.hist(data, weights = weights)
plt.ylabel("Percent / bin (5mA)")
plt.xlabel("Offset [mA]")
#plt.show()
plt.savefig("offsets_prototypes.png")

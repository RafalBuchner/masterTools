colors = [
            (.5,1,.5),
            (.7,.6,1),
            (1,.05,.4),
            (.45,.65,1),
            (.3,1,.25),
            (.1,.4,.6),
            (1.,.65,.3),
            (1,0.1,0.0),
            (.95,.85,0),
            (0.5,0.75,1.0),
            (0.45,0.5,.5),
            (0.95,.45,.35),
            (0.45,1,1),
            (.3,1,.4),
            (.6,.75,1),
            (.15,.05,.6),
            (.8,1,.75),
            (.65,.85,0),
            (.3,.15,.5),
            (.7,.75,1),
            ]

for i, color in enumerate(colors):
    fill(*color)
    rect(0,50*i,50,50)

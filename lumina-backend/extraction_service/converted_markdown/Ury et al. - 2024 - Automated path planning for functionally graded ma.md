Full Length Article 
Automated path planning for functionally graded materials considering 
phase stability and solidification behavior: Application to the 
Mo-Nb-Ta-Ti system 
Nicholas Ury *, Brandon Bocklund , Aurelien Perron , Kaila M. Bertsch 
Materials Science Division, Lawrence Livermore National Laboratory, Livermore, CA 94550, USA   
A R T I C L E  I N F O   
Keywords: 
functionally graded material 
CALPHAD 
Additive Manufacturing 
crack susceptibility 
Phase stability 
A B S T R A C T   
Functionally graded materials have the potential to improve upon monolithic parts by locally tailoring com­
positions to surrounding environmental conditions. Difficulties arise when designing composition gradients as 
incompatible materials can result in detrimental phase formation and failure of the gradient joint. As many alloys 
are multi-component, designing a composition gradient free of detrimental phases is difficult due to the large 
composition space available to explore. A framework was developed that improves the path planning algorithm 
and surrogate models with adaptive sampling schemes specific to their problem definition. A cost function was 
created to minimize a property (such as cracking susceptibility) along a path. This framework was applied to the 
Mo-Nb-Ta-Ti system as a case study to showcase the efficiency in building the surrogate models and in iterating 
different optimal compositionally graded paths.   
1. Introduction 
Materials in extreme environments generally require several 
different optimized properties. For example, aerospace applications 
require high temperature or corrosion resistance, strength and low 
density. Finding materials that can satisfy all these requirements is 
difficult, so different materials can be joined together to satisfy these 
spatially dependent requirements. As an example, high temperature 
resistant Ni- or Co-based superalloys can be joined with low density and 
high specific strength Ti- or Al-alloys [1]. Traditional fabrication of 
these joints utilizes either fastening or welding techniques which involve 
extensive manufacturing time and increases the risk of failure compared 
to single monolithic parts. Fabricating joints as a single component with 
a smooth compositional gradient, known as a functionally graded ma­
terial (FGM), has the potential to alleviate these issues [1,2,3]. Other 
applications that can benefit from FGMs include light water nuclear 
reactors (connecting high strength pressure vessels to high oxidation 
and creep resistant superheater tubes) or magnetically confined fusion 
reactors (high melting temperature, low erosion rate and limited tritium 
retention plasma-facing side with a high thermal conductivity backing) 
[1,4,5,6,7,8]. In addition, bulk properties of an FGM can be tuned by 
optimal placement of dissimilar materials [9]. 
Additive manufacturing (AM) via directed energy deposition (DED) 
provides an avenue to fabricate FGMs due to its ability to produce 
flexible geometries and retain local control over composition or micro­
structural features [1,2,3]. However, production of FGMs presents 
several design challenges. The simplest way of designing an FGM is to 
grade the composition linearly between the two alloy compositions. 
While some pairs are compatible with each other and can be manufac­
tured with such a composition gradient, many alloy pairs will result in 
the formation of brittle or detrimental phases in a linear gradient, thus 
compromising the integrity of the joint [10,11,12,13]. For example, a 
linear gradient between Ti64 and SS304L would result in intermetallics 
such as FeTi, Fe2Ti, Ni3Ti and NiTi2, which results in crack formation 
along the gradient during the build process [13]. In addition, the large 
variance in liquidus along the gradient can result in subsequent melting 
of previous layers (below the topmost layer) and overflow of these layers 
to the side of the gradient joint [13]. The Calphad method was shown to 
provide good prediction of phase formation when compared to experi­
mental observations and it was suggested that the Calphad method could 
be useful in designing gradient paths that avoid formation of detrimental 
phases [12]. This concept was realized in the development of a gradient 
path between Ti64 and SS316L with a path of Ti64 → V → Cr → Ni-20Cr 
→ SS316L [14,15,16]. The Calphad method was also used to reduce 
* Corresponding author. 
E-mail address: ury3@llnl.gov (N. Ury).  
Contents lists available at ScienceDirect 
Computational Materials Science 
journal homepage: www.elsevier.com/locate/commatsci 
https://doi.org/10.1016/j.commatsci.2024.113172 
Received 3 May 2024; Received in revised form 7 June 2024; Accepted 9 June 2024   
Computational Materials Science 244 (2024 ) 113172 
Available online 15 June 2024 
0927-0256/© 2024 Elsevier B.V. All rights are reserved , including those for text and data mining , AI training , and similar technologies. 


cracking in an SS316L-IN718 FGM. Laves phases were observed at 
around 78–98 % SS316L along the gradient resulting in crack formation 
during the build process [17]. Calphad predictions showed that adding 
pure nickel to this region would reduce laves formation, which allowed a 
crack-free FGM to be fabricated. 
Solidification behavior can also be predicted using Calphad. Usage of 
the Scheil-Gulliver model allows for prediction of solute redistribution 
between the liquid and solid phases (and by extension, phase formation 
upon solidification) under the assumption that no diffusion occurs in the 
solid phase and infinitely fast diffusion occurs in the liquid phase 
[18,19]. The Scheil-Gulliver model has been observed to predict phase 
formation better than equilibrium when assessing gradient joints such as 
Ti to Invar and Ti64 to Invar [20]. The usage of the Scheil-Gulliver 
model has been extended further to project phase formation upon so­
lidification onto ternary phase diagrams to aid in designing composition 
pathways to avoid deleterious phase formation during rapid solidifica­
tion and thermal exposure [16]. The Scheil-Gulliver model can also be 
used to qualitatively assess phenomena like solidification cracking sus­
ceptibility, for example, a printable FeCrAlNiMo alloy was designed by 
minimizing the freezing range and the Kou cracking index [21,22]. The 
freezing range was minimized to limit liquation cracking by minimizing 
the amount of chemical segregation and prevent remelting of inter­
dendritic regions upon deposition of successive layers, while the Kou 
cracking index was minimized to reduce the susceptibility to solidifi­
cation cracking [21]. Comparison of different cracking indices found in 
literature such as the freezing range, cracking susceptibility coefficient 
(CSC), Kou cracking index, improved CSC (iCSC), and the simplified 
Rappaz-Drezet-Gramaud (sRDG) model on various AM gradient joints 
suggested that the Kou cracking index, iCSC, and sRDG criteria provide 
the best agreement with experimental data on where crack formation 
could occur in a gradient joint [22,23,24,25]. 
The works described above designed gradient paths by manually 
assessing relevant binaries and ternaries. However, this requires 
knowledge and understanding of all the subsystems and considering 
them simultaneously. Viable paths may also only exist in a quaternary 
composition space or even higher component spaces that cannot easily 
be visualized. By treating composition path planning as a robotic path 
planning problem, algorithms used in robotic path planning can be re- 
formulized to apply to FGM design [26,27,28]. Utilizing these algo­
rithms allows for the usage of cost functions to determine an optimal 
gradient path. Beyond minimizing detrimental phase formation, it could 
be useful to design composition gradients with monotonic properties 
[28]. For example, non-monotonic gradients in the thermal expansion 
and strength or ductility along a gradient will produce large thermal 
stresses that can reduce the integrity of the joint. Cost functions that 
favor monotonic gradients can be applied to the path planning algorithm 
to ensure that these properties monotonically increase or decrease along 
the gradient path. By doing so, the gradient of the property along the 
path can be directly tuned to avoid drastic changes or even mapped to 
produce any property profile. 
Given the importance of solidification behavior on additive 
manufacturing, designing functionally graded materials must account 
for the printability of compositions along the gradient path. Therefore, 
this study introduces a new cost function that aims to minimize a 
property (in this study, the cracking susceptibility) along the gradient 
path. When path planning in high dimensional space, surrogate models 
can be used to improve performance and reduce the number of expen­
sive computations. As path planning is done in composition space, the 
property surrogate models in this work will be designed to take 
advantage of the simplex-nature of the composition space. Furthermore, 
a phase classification surrogate model will also be developed, which 
utilizes information about phase equilibria to efficiently assess the 
boundaries of the classification model. Finally, a case study in calcu­
lating optimal gradient paths in the four-component Mo-Nb-Ta-Ti sys­
tem while minimizing the solidification cracking susceptibility and 
avoiding certain phases will be performed. 
2. Computational details 
2.1. Problem description 
The goal of designing an FGM for AM is to find a path between two 
desired composition endpoints that a) is within the feasible composition 
space and b) optimizes a given cost function. The feasible composition 
space is any composition that is determined to be printable, defined in 
this work as regions where deleterious phases formation is not ther­
modynamically favorable. In general, the infeasible space could be 
defined as any composition that will likely lead to undesirable features 
in a printed part (for example, compositions rich in an element with high 
oxygen affinity). 
Obstacle functions can be created to represent what compositions to 
avoid when creating a functionally graded path. Obstacles are bound­
aries that separate the feasible composition space from the infeasible 
space, where an obstacle function will return true or false for whether a 
composition is inside or outside the feasible composition space. 
Cost functions are used to compare different gradient paths to 
determine which one is more likely to give desirable results. They are 
defined from a path between two compositions, where a lower cost 
suggests a more optimal path. Several types of cost functions can be used 
for designing functionally graded materials which include a shortest 
path length (equation (1), where p is the path coordinate between nodes 
N1 and N2), a safest path length (equation (2), where distance(p) is the 
closest distance to the obstacle boundary), or property monotonicity 
(lack of increasing defined in equation (3) and lack of decreasing in 
equation (4), with df
dp being the derivative of a function with respect to 
the path coordinate) [27,28]. A new cost function is implemented in this 
study that minimizes a property along the path (equation (5)). Equation 
(5) is split into two parts: integrating both the property and the property 
multiplied by its derivative along the path. The first part of the equation 
penalizes high property values, thus favoring a path that traverses lower 
values. However, since it is also dependent on the path length, a 
consequence of this term is that it could favor a short path encountering 
a high property value over a longer path encountering a low property 
value. Thus, the second part of the equation is added to penalize large 
property gradients in the path. In high gradient regions, considering 
only the property gradient in the cost function could result in the path 
oscillating to traverse the high gradient region while minimizing the 
property gradient along the path (this is analogous to a switchback road 
that goes back and forth up a steep hill to reduce the grade of the road). 
To prevent this behavior, the property gradient is multiplied by the 
property value to increase the cost if the path stays and oscillates in 
Fig. 1. a) arbitrary function f(p) along a path with schematics of how different 
cost functions are computed: b) lack of increasing (equation (3), c) lack of 
decreasing (equation (4) and d) minimizing property (equation (5). 
N. Ury et al.                                                                                                                                                                                                                                     
Computational Materials Science 244 (2024 ) 113172 
2 


composition along a low gradient. The addition of the first part of the 
equation also prevents the cost function from being 0 if the property 
gradient is 0 at a large property value. 
Schematics of equations 3–5 are shown in Fig. 1 where the lack of 
increasing cost function integrates all regions where the slope is nega­
tive, the lack of decreasing cost function integrates all regions where the 
slope is positive, and the minimizing property cost function considers 
both positive and negative slopes. 
C =
∫N2
N1
dp = l
(1)  
C =
∫N2
N1
1
distance(p) dp
(2)  
C =
∫N2
N1
max
(
−df
dp, 0
)
dp
(3)  
C =
∫N2
N1
max
(df
dp, 0
)
dp
(4)  
C =
∫N2
N1
f
(
1 +
⃒⃒⃒⃒
df
dp
⃒⃒⃒⃒
)
dp
(5)  
2.2. Phase classification model 
Creating an obstacle model for the path planner to avoid detrimental 
phase formation requires knowing what regions in the composition 
space result in these phases being stable. One option would be to 
perform grid sampling in the composition space; however, this can waste 
a lot of computations as only the phase boundaries need to be known. 
Constraint satisfaction algorithms also exist where a classifier model is 
built up by searching outward perpendicular to the model boundary 
until the true boundary is found. This is continued until a sufficient 
number of samples are generated that adequately represent the true 
phase boundary [29,30]. Due to a lack of a termination criteria, the 
number of samples required for fitting the constraint satisfaction algo­
rithm is determined by the user. While this method can be generalized to 
different types of constraints, it is inefficient when assessing phase sta­
bility as it only considers whether the input phases are stable or not and 
ignores additional information that may be generated during equilib­
rium calculations (such as compositions or phase fractions of each stable 
phase in equilibrium). Thus, a large number of samples would be 
required to create an obstacle using the constraint satisfaction algo­
rithm. In this work, an adaptive surrogate model was developed to take 
advantage of phase boundary information to efficiently fit an obstacle 
model for each phase of the system with less samples. 
In any multi-phase equilibrium, the composition of each phase cor­
responds to a vertex of the tie-hyperplane for the phase equilibrium. 
These tie-vertices are points on the phase boundary where for a given 
phase, the point represents the composition at which the phase fraction 
of that phase is one. A surrogate model of these boundaries can then be 
constructed to divide the composition space into regions where a 
particular set of deleterious phases are stable and where they would be 
metastable. For a single deleterious phase, the obstacle model becomes 
the phase boundary surface; however, if multiple deleterious phases are 
considered, then the obstacle model becomes the union of the phase 
boundary surfaces for each phase. Sampling compositions in multi- 
phase regions will improve an obstacle model more efficiently than 
sampling in single-phase regions because single-phase regions only give 
a binary indication whether a phase is stable or not at a given compo­
sition, while compositions in a multi-phase region directly generate 
points on an obstacle boundary for all phases present at a given 
composition. 
For each phase in the system, a support vector machine (SVM) was 
used to classify the regions where a phase was stable (including both 
single- and multi-phase regions) versus where it was unstable, mapping 
out both the composition and temperature space. As each phase was 
modeled with its own SVM, the intersection or union of different SVM 
models can be used to represent multi-phase regions, allowing flexibility 
over how the obstacle model is defined without having to retrain the 
phase classification model. For example, if two phases (α and β) were 
deleterious and wanted to be avoided, then the obstacle model would be 
defined as the union of the SVM models for phase α and β. As another 
example, if the path planner were to be constrained to where both α and 
β are stable, then the obstacle model would be defined as the comple­
ment of the intersection of the two SVM models. 
When defining the SVM model, the compositions are separated into 
two classes to define the unstable and stable regions of a phase and are 
labeled as either −1 or 1 respectively. Then fitting the SVM model in­
volves finding a model such that sign
(
wTφ(xi) +b
)
will correctly classify 
each composition as to whether the phase is stable or not (where w are 
the weights for each composition xi, φ(xi) is the location of composition 
xi in feature space and b is a constant [31]). Fitting the SVM model in­
volves two terms (equation (6)): a) minimizing wTw, which maximizes 
the margin between the two classes of compositions and b) minimizing 
C∑
iξi which minimizes the penalty for falsely classifying a composition 
(where ξi represents some allowable distance from the margin that a 
composition is allowed to be and C represents the strength of the penalty 
term. This margin is represented as the constraint in the minimization 
problem where yi is the label of the data point xi. In this work, a gaussian 
radial basis function is used (shown in equation (7)) with γ controlling 
the influence of nearby data points on the kernel output. As a kernel, 
equation (7) for compositions xi and xj can be transformed to be the 
inner product of the xi and xj in the feature space as shown in equation 
(8). 
minimize
1
2wTw + C
∑
iξi
subject to
yi
(
wTφ(xi) + b
)
≥1 −ξi
ξi ≥0
(6)  
k
(
xi, xj
)
= exp
(
−γ‖xi −xj‖2)
(7)  
k
(
xi, xj
)
=
〈
φ(xi)φ
(
xj
)〉
(8)  
Construction of the SVM model starts by generating a few starting points 
based on two criteria to provide initial guesses of the phase boundaries 
for the adaptive sampling. First, points are added at the end points of the 
composition space (pure elements). Second, the Gibbs free energy sur­
face of each phase is sampled, and the minimum and maximum of the 
mixing Gibbs free energy are chosen. These points represent potential 
regions where a phase can be stable or regions where a miscibility gap 
can occur. This creates c +2n starting points where c is the number of 
components and n is the number of phases in the system. For mapping a 
range of temperatures, these samples are generated at temperatures 
between the range separated by a constant interval. This specific method 
of generating the initial starting points is arbitrary (chosen here as it 
performed better than random sampling); any method for generating 
these points can be used. 
Equilibrium is computed for each initial sample. If a sample is in a 
single-phase region, the composition (and temperature, if it is being 
mapped) is added to the phase model of the stable phase as an accepted 
point. This composition is also added to all other phase models as a 
rejected point. If the sample is in a multi-phase region, the composition 
of the sample is added to the models of each stable phase as an accepted 
point. Then, the compositions at the phase boundaries (taken from the 
equilibrium calculations) are added to the corresponding phase model as 
both an accepted and rejected point to explicitly define the phase 
boundaries. 
After the starting points are added to the phase models, the models 
N. Ury et al.                                                                                                                                                                                                                                     
Computational Materials Science 244 (2024 ) 113172 
3 


are fitted to generate an initial estimate of the phase equilibria of the 
system. New samples to be added to the phase classification model are 
generated using a best candidate sampler [32,33]. This sampler has been 
observed to scale to higher dimensions while maintaining low discrep­
ancy in the generated samples [32]. A sample is generated by first 
generating candidates, then comparing the distance of the candidates to 
the closest of the previous samples, and, finally, selecting the candidate 
that maximizes this distance. The samples generated from the best 
candidate sampler are then filtered out by only accepting candidates 
that are either outside the region of all SVM models (which represents 
unexplored regions) or inside the region of two or more SVM models 
(representing multi-phase regions where phase boundary information 
for each stable phase can be extracted). The process of generating can­
didates and filtering them to create new samples is repeated until a 
desired number of samples is reached (in this work, 10 samples were 
selected to add as a batch for the classification model). There are cases 
where these regions of interest are small, and many iterations are 
required to generate the desired number of samples. For these cases, a 
limit on the number of attempts made to generate samples is set and if 
the number of attempts exceeds this limit, the rest of the samples are 
generated by the best candidate sampler without any filtering from the 
SVM models. The new samples are then added to the model the same 
way the initial compositions were added: calculating equilibrium, 
checking if multiple phases are system, then adding the sampled 
composition along with the compositions at the phase boundaries to the 
SVM models. The SVM models are then updated, and this process repeats 
until a desired number of compositions are evaluated. Further devel­
opment is needed to define a termination criterion, but it may be 
possible to compare the predictions to the generated samples until a 
certain accuracy is reached. 
2.3. Property surrogate model 
While the phase classification model can utilize the phase composi­
tions at equilibrium, properties are generally scalar values, in which no 
additional information can be obtained computing a property at a spe­
cific composition and temperature. Mapping properties over composi­
tion space can be done by a grid sampler, where the composition space is 
divided into evenly spaced segments and the properties are calculated at 
each composition on the mesh. This scheme, however, becomes ineffi­
cient at higher dimensions. Table 1 shows the number of samples needed 
to map the composition space using a grid sample with composition 
steps of 2 at.%. The number of samples needed increases exponentially 
with the number of components. 
An adaptive surrogate model was created in place of the grid sam­
pling where samples were chosen which best improves the surrogate 
model in order to reduce the number of required samples for mapping 
out the composition space. Radial basis function interpolation was used 
for the surrogate model due to its simplicity, as shown in equation (9) 
where βi are the weights for the basis functions (ϕ), fj are polynomials, 
and γj are fitted weights for the polynomials. It interpolates between the 
training dataset using a linear combination of basis functions, which are 
functions of the Euclidean distance between the evaluation point and the 
training dataset shown in equation (10) where xj is the interpolation 
point and Zi is the composition of a sampled point [34,35]. In this study, 
a cubic basis function (ϕ(r) = r3) was used given its smoothness, 
differentiability, and lack of dependence on a scaling term [35]. The 
polynomial fj was taken to be fj = 1 to represent the mean of the 
interpolated surface. An additional constraint during fitting was added 
as ∑βi = 0, which must be satisfied for cubic basis functions as they are 
conditionally positive definite [35]. The linear system that was solved to 
fit the radial basis function interpolation is given in equation (11), where 
R and F are the matrices of the basis function and polynomial term 
between the training samples and Y are the function responses at Z. 
s(x) =
∑
iβiϕ
(
rij
)
+
∑
jγjfj(x)
(9)  
rij =
⃦⃦xj −Zi
⃦⃦
(10)  
[
R
F
FT
0
][
β
γ
]
=
[
Y
0
]
(11)  
Adaptive sampling is done through both exploration and exploitation 
sampling. In the exploration phase, candidate samples are weighed by 
their minimum distance from the training dataset (equation (12)). In the 
exploitation phase, samples are weighted both by a power function 
(which describes how the candidate samples are spaced from the 
training dataset) and the second derivative (where regions of high cur­
vature may need more samples) given in equations 13–16 [34,36]. In 
equations (14) and (15), r and f are the matrices of the basis function 
and polynomial term between the training samples and evaluation point 
x. In equation (16), a small value (ε) is added to the second derivative so 
that the exploitation criterion is always non-zero. 
Cg(x) = min‖x −Zi‖
(12)  
P2(x) = ϕ(0) + uTFTR−1Fu −rRrT
(13)  
u = FTR−1rT −f
(14)  
N = βTRβ
(15)  
Cl(x) =
( ⃒⃒∇2s
⃒⃒+ ε
)
P2N
(16)  
These two criteria are normalized and summed together through an 
additional weight α by equation (17). This weight is modified during 
cross validation, where if the normalized root mean square error for 
cross validation (RSMECV) (between the true value ̂yi calculated at xi 
and predicted value yi if training sample xi is removed from the model, 
equation (18) increases after the next batch of samples, then α will in­
crease and the weight of the candidate samples will favor exploration. If 
the RSMECV decreases, then the weight of the candidate samples will 
favor exploitation more [36,37]. The changes in α due to the new error is 
given in equation (19). This process repeats until the root mean square 
error is below a given threshold, indicating that the addition of the most 
recent samples only improved the model by a minimal amount. 
C(x) = αCg(x) + (1 −α)Cl(x)
(17)  
RSMECV =
̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅
1
n(yi −
̂yi)2
√
maxy −miny
(18)  
α = 0.99*min
(
0.5* en
en−1
, 1
)
(19)  
The geometry of the n-component composition space is an (n-1)-simplex 
(with the n vertices representing the pure components), where a face on 
the simplex represents any of the (n-1)-component space. A surrogate 
model fitted for n-components should be able to predict behavior in any 
of the lower order systems (m-component space where m < n). Fitting 
the model on the n-component space without any assumptions on how 
Table 1 
Sampling density given the number of components at 2 at.% steps in 
composition.  
Number of Components 
Number of samples needed with 2 at.% stepping 
2 
51 
3 
1,326 
4 
23,426 
5 
316,251 
6 
3,478,761  
N. Ury et al.                                                                                                                                                                                                                                     
Computational Materials Science 244 (2024 ) 113172 
4 


this space is related to the lower order systems could result in a poor fit 
on the lower order systems as the adaptive model would likely be 
extrapolating. In this work, the adaptive model was built by fitting all 
the lower order systems starting with the least number of components 
until reaching to all the components (fitting unaries, then binaries, then 
ternaries, etc.). For a given lower order system defined by m-compo­
nents, the samples for each m-component system will be used as starting 
points to fit the (m + 1)-component system (a schematic of this is shown 
in Fig. 2. By adding these samples on the faces of the (m + 1)-component 
system, the adaptive model can better extrapolate to the (m + 1)- 
component system as well as retain accuracy on each m-component 
system. 
2.3.1. Crack susceptibility modeling 
The surrogate model is discussed in section 2.3. was used to create a 
model for crack susceptibility predictions. This was to reduce compu­
tational time of the path planning as computing cracking susceptibility 
from Calphad models are relatively expensive compared to retrieving 
them from a surrogate model. AM induces large thermal gradients and 
rapid solidification, which can lead to defects in a part if an alloy has a 
high cracking susceptibility. In an FGM, every step along the composi­
tion gradient is a new alloy which must be assessed for susceptibility to 
cracking. Cracks that form at a single step along the gradient reduce the 
mechanical integrity of the entire gradient component, even if they do 
not propagate throughout the rest of the build. Cracking susceptibility 
can be treated as a cost function where the path planner tries to mini­
mize equation (5). 
Cracking susceptibility may be estimated from the fraction of solid 
vs. temperature curve obtained from the Scheil-Gulliver solidification 
model. The freezing range (equation (20)) takes the difference between 
the temperature at which solid starts to form (TL) and the temperature at 
which the last liquid solidifies (Ts). The cracking susceptibility criteria 
(CSC, equation (21)) compares the time between the second and third 
solidification stage, where longer time spent in the third solidification 
stage increases the likelihood of cracking [24]. The time is assumed to be 
proportional to the temperature given a constant cooling rate and xi is 
the fraction of solid whereas Txi is the temperature at xi. The values for 
x1, x2 and x3 were taken as 0.99, 0.9 and 0.4 respectively. The Kou 
cracking criteria takes the slope of the temperature versus the square 
root of the fraction of solid towards the end of the solidification 
(equation (22)) [22]. This criterion assumes cracking to take place when 
the lateral growth of dendrites towards the end of solidification is slow, 
leading to long channels of interdendritic regions that are hard to fill if 
cracking occurs. The values for x1 and x2 were taken as 0.98 and 0.93 
respectively. The improved CSC and simplified Rappaz-Drezet-Gremaud 
criteria (equations (23) and (24)) places an emphasis on the end of 
Fig. 2. Schematic of how training data from lower order systems are incorporated into higher order systems to fit the adaptive surrogate model. For the ternary and 
quaternary system, data on a single “face” on each system is shown for clarity. 
Fig. 3. Schematics of a) freezing range, b) crack susceptibility criteria, c) Kou cracking, d) improved CSC and e) simplified Rappaz-Drezet-Gremaud criteria.  
N. Ury et al.                                                                                                                                                                                                                                     
Computational Materials Science 244 (2024 ) 113172 
5 


solidification where the likelihood of cracking is the highest [23]. The 
values for x1 and x2 were taken as 0.7 and 0.98 respectively. A schematic 
of these criteria is shown in Fig. 3. A comparison of these different 
criteria on different additively manufacturing gradients suggested that 
the Kou, iCSC and sRDG methods gave the best predictability out of the 
five criteria as these methods focus highly on the end of the solidification 
behavior [25]. Thus, only these three criteria were used in this work for 
path planning. 
FR = ΔT = TL −TS
(20)  
CSC = TX1 −TX2
TX2 −TX3
(21)  
Kou =
⃒⃒⃒⃒⃒
dT
d
(
̅̅̅
fs
√)
⃒⃒⃒⃒⃒
̅̅
fs
√
→1
≈
⃒⃒⃒⃒
TX1 −TX2
̅̅̅̅̅
X1
√
−
̅̅̅̅̅
X2
√
⃒⃒⃒⃒
(22)  
iCSC =
∫TX2
TX1
fs(T)dT
(23)  
sRDG =
∫TX2
TX1
fs(T)2
(1 −fs(T) )2 dT
(24)  
2.4. Path planning algorithm 
Techniques from robotic path planning may be applied to develop 
viable composition paths for functionally graded materials. As an 
analogous method, regions where detrimental phases are stable can be 
considered obstacles in the path planner. In addition, cost functions can 
be added to determine an optimal path. These cost functions can include 
creating a safest path (one that strays from all obstacles as far as 
possible) and optimizing property variations (e.g. minimizing cracking 
susceptibility). Two common approaches used in robotic path planning 
are the probabilistic road map (PRM) and rapidly-exploring random 
trees (RRT). In this study, a new path planning algorithm was developed 
that combines PRM and RRT methods to circumvent their respective 
limitations. The PRM algorithm was used to generate an initial feasible 
path between two selected compositions, and the RRT algorithm was 
used to further optimize the path. The following will describe both al­
gorithms separately, their limitations, and how combining the two 
methods can overcome these limitations. 
The PRM algorithm is split into two phases: a learning phase and a 
query phase. In the learning phase, compositions in the feasible search 
space (as defined in 2.1) are sampled (which can be done using rejection 
sampling, removing any samples generated within an obstacle bound­
ary) and an undirected graph between the compositions is created 
(Fig. 4a and b). When creating this graph, edges are added connecting 
each composition to all nearby sampled compositions within a specified 
radius. This undirected graph represents all possible paths between any 
two compositions (Fig. 4c). In the query phase, an optimal path in the 
graph is found between two selected compositions as shown in Fig. 4d 
(the initial and final composition for this case). The optimal path chosen 
from the graph is chosen based off shortest path algorithms, specifically 
Dijkstra’s algorithm in this work [38]. Note that the shortest path in this 
work refers to the path that minimizes the cost (which can include 
distance) between the two endpoints. If no path between the initial and 
final composition can be found, another learning phase starts, and more 
compositions are added to the graph. This is repeated until a path can be 
found. If a path cannot be found in the feasible search space, it is possible 
to redefine the obstacle function as a cost function to be used for a safest 
path, then the optimal path will be the one that minimizes the length of 
the path in the infeasible search space. The PRM algorithm is probabi­
listically optimal such that, as the number of samples approaches in­
finity, the most optimal path will be found [39,40]. This method can 
quickly find a path (without any guarantee that it is the optimal path) as 
it considers all sampled compositions when searching for a path. 
Fig. 4. Schematic of probabilistic roadmap algorithm: a) define path planning problem with initial and final compositions, obstacle and cost functions, b) sample the 
feasible search space, c) create network connecting nearby sampled compositions, d) find the best path in the network. 
N. Ury et al.                                                                                                                                                                                                                                     
Computational Materials Science 244 (2024 ) 113172 
6 


However, it suffers from being limited in improving the initial path. 
When adding new compositions to the network, distance must be tested 
among all previous compositions to see if an edge can be added. As more 
compositions are added, the number of distance calculations required 
increases linearly. Subsequently, when finding the optimal path with the 
new compositions, the time complexity of Dijkstra’s algorithm increases 
non-linearly with the number of sampled compositions and edges as 
O((E + V)log(V) ), where V is the number of compositions and E is the 
number of edges between compositions [38,41]. Given that the PRM 
algorithm considers all candidate compositions in the network, the 
computation performance of the PRM suffers significantly as more 
compositions are sampled. 
While the PRM algorithm builds the path in two separate and distinct 
steps, the RRT algorithm builds the path incrementally. A graph is 
initially created with the first node as the initial composition. A new 
composition is then sampled in the feasible space and the nearest node 
to the new sample is found. If an edge can be created between the 
nearest node and the new composition while avoiding all obstacles, then 
the edge and composition will then be added to the graph. This process is 
repeated until the final composition is reached [42]. The RRT algorithm 
itself does not account for cost functions and cannot create an optimal 
path. A variation of this algorithm (RRT*) allows for modification of the 
graph to optimize the path as it is being created [43]. In RRT*, when a 
sample is generated, multiple nearby nodes are tested, and an edge is 
created between one of the nodes and the new sample that minimizes the 
cost going from the initial composition to the new sample (Fig. 5a). An 
additional rewiring step is performed after the sample is added to the 
graph. This step searches for nearby nodes from the new sample and a 
potential path from the initial composition to the nearby node going 
through the sample is evaluated (Fig. 5b). If this potential path to the 
nearby node has a lower cost than the current path going to the nearby 
node, then the graph is rewired with the new path. This can be done for a 
number of iterations even after a path between the initial and final 
compositions are found in order to further optimize the path (Fig. 5c and 
d). 
Another variation of the RRT algorithm exists called the RRT*FN 
algorithm. This is similar to RRT*; however, a limit is placed on the 
number of nodes in the graph to reduce memory usage. If the number of 
nodes in the graph exceeds this limit, a dangling node (a node that does 
not have an edge leading out of it) is removed [44]. As with the PRM 
algorithm, the RRT* and RRT*FN algorithms are probabilistically 
optimal with an optimal solution being guaranteed as the number of 
samples approaches infinity. The RRT*FN algorithm has a lower time 
complexity when updating an initially found path than the PRM algo­
rithm, as both the number of sampled compositions and the number of 
edges is limited. As the path is optimized incrementally, the use of 
Dijsktra’s algorithm can be avoided as a new path does not have to be 
found on the graph each time. However, the RRT algorithm has been 
reported to be inefficient in finding a path when the feasible search 
space has narrow openings for the path or dead ends [45]. In these 
scenarios, random sampling of compositions in the feasible search space 
is likely to encounter two possibilities. The first is that the new 
composition cannot be added to the path as an obstacle is between the 
two. Second, it is likely that the new composition will not get the path 
closer to the final composition. 
2.4.1. Combining the two methods 
This study developed a novel path planning method combining PRM 
and RRT*FN algorithms to mitigate the inefficiencies during both the 
initial path finding and the path optimization steps. The path planning 
process in this work was split into first finding an initial, viable path 
between the initial and final compositions, then optimizing that path. 
The PRM algorithm was used when finding the initial path as it is able to 
sample a large number of potential paths between the initial and final 
components. Once the initial path is found, the compositions that are not 
part of the initial path are removed and the remaining path is used as a 
starting point for RRT*FN to optimize the path. During RRT*FN, new 
compositions are sampled with a bias to be generated near the current 
path to improve the likelihood of being added to the path. As the path is 
improved incrementally, this bias is constantly updated to sample near 
the current state of the path (which cannot be done in PRM as the path is 
only known after the query phase). 
When rewiring a tree during RRT*FN, the evaluated cost functions 
are stored in both the edges and nodes to avoid repeating calculations 
when evaluating the cost of a new node. Each edge will store the cost 
between the initial and final nodes that it joins, while each node will 
store the cost of the entire path from the initial configuration to the 
current node. Evaluating the cost of adding a new node becomes the sum 
of the cost at the current node and the cost of the edge between the 
current and new node, where the only new computation needed is the 
cost of the new edge. After rewiring, the cost of all successive nodes from 
the rewired node must be updated with the new cost from the initial 
node to the rewired node; however, this does not require additional 
evaluations of the costs function for pre-existing edges. 
3. Results and Discussion: Application to the Mo-Nb-Ta-Ti 
system 
The methods described in section 2 were used on the Mo-Nb-Ta-Ti 
system as a case study showing the efficiency of the phase classifica­
tion model and the adaptive surrogate model as well as the flexibility of 
the path planner in switching between different obstacle and cost 
functions. 
3.1. Surrogate model validation 
Before performing the path planning activity, surrogate models for 
solidification cracking criteria and phase classification were created. 
Surrogate models for solidification cracking were created for the Kou, 
iCSC and sRDG cracking criteria. The Scheil-Gulliver simulations were 
conducted using pycalphad and the pycalphad-scheil package [46,47]. 
For training both the phase classification model and the adaptive sur­
rogate model, an thermodynamic database of the Mo-Nb-Ta-Ti system 
was used that modeled the binary systems and assumed no excess 
ternary interactions [48,49,50]. No ternary interactions parameters 
were assumed given that modeling only the binaries gave decent 
Fig. 5. Schematic of RRT* algorithm showing sequential steps of generating a 
sampling composition near the current optimal path and either rejecting 
because the new composition does not improve the current path or adding and 
rewiring to improve path. 
N. Ury et al.                                                                                                                                                                                                                                     
Computational Materials Science 244 (2024 ) 113172 
7 


agreement with the limited data found regarding the liquidus and soli­
dus in the ternary composition spaces [51,52,53]. 
The phase classification model (section 2.2.) was constructed using a 
gaussian radial basis function as the kernel, a value of γ as 50, and C as 
1000. A total of 5000 samples (which included composition and tem­
perature in the quaternary space between a temperature range of 
500–1500 K) were used, with the SVM models for each phase updating 
after the addition of every 10 samples. To assess the validity of the phase 
classification model, 1000 random samples were generated, and the 
stable phases calculated from equilibrium and predicted from the phase 
classification model were compared, with the success rate defined as the 
number of correct predictions over the total number of points tested. 
This was done 100 times and gave a prediction accuracy of 91.53 ± 0.62 
%. 
The adaptive surrogate model (section 2.3.) was constructed by 
creating surrogate models for each unary, binary, ternary and quater­
nary in increasing order. For the unaries, the surrogate model consisted 
of a single point, which was 0 given that the cracking index for each 
method gives a value of 0 for pure elements. These data points plus 10 
extra randomly generated compositions were used to start the surrogate 
models for each binary. The extra compositions were mainly used to 
create a rough estimate of the maximum and minimum of the cracking 
indices along the binary to give a better assessment of the cross- 
validation error. When fitting the surrogate model, a candidate 
composition was found by generating 10,000 random compositions and 
choosing the sampling that maximized equation (17) and was added to 
the model. After every 5 compositions, the cross-validation error was 
calculated by averaging the error in the model at the 5 compositions if 
they were excluded from the model. This process of adding compositions 
and checking the cross-validation error was repeated until the cross- 
validation error (equation (25) was less than 0.02. When all the bi­
nary systems were fitted, the compositions and cracking indices were 
used to initialize the ternary surrogate models along with 10 extra 
compositions (as was done for the fitting the binary systems). The 
ternary surrogate models were fitted using the same method as fitting 
the binary system. The quaternary surrogate model was fitted using the 
final ternary surrogate models as a starting point and following the same 
procedure as fitting the binary and ternary systems. 
RMSE =
1
maxftrue −minftrue
̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅
∑(
f i
pred −fi
true
)2
N
√
√
√
√
(25)  
To assess the validity of the adaptive model, grid sampling was per­
formed at 2 % steps in composition over the quaternary Mo-Nb-Ta-Ti 
space sampling 23,426 points in total. With the adaptive model, the 
convergence criteria of RMSE = 0.02 were reached with 299 samples for 
the Kou cracking criteria, 239 for the iCSC criteria, and 264 samples for 
the sRDG criteria. For simplicity, comparison between the adaptive 
model and grid sampling is only shown for the Kou cracking criteria, as 
in Fig. 6 and Fig. 7, respectively. Training points in the adaptive model 
are also overlaid on the model prediction plots. A visual comparison 
between the grid sampling and the surrogate model shows general 
agreement despite using less than 1.5 % of the number of samples 
generated using grid sampling. Fig. 8 shows the relative error of the 
adaptive model and the grid sampling using equation (26). Most of the 
composition space in the four ternaries shows a relative error of < 5 %. 
The few regions with high relative error appear to correlate with the 
non-smooth regions observed from the grid sampling, which may be 
caused by minor numerical differences when computing the Scheil so­
lidification simulations. These regions are smoothed out by the surro­
gate model, which results in a large relative error. 
ε =
⃒⃒⃒fpred −ftrue
⃒⃒⃒
maxftrue −minftrue
(26)  
Comparing all the grid samples to the adaptive model, the adaptive 
model showed a root mean square error of around 5.1 % (using equation 
(25)). This behavior was similar for both the iCSC and sRDG cracking 
methods. The RMSE of the adaptive model is higher than the threshold 
used for fitting the model, likely due to all the samples being assessed, 
Fig. 6. Kou cracking criteria for the four ternaries in the Mo-Nb-Ta-Ti system 
predicted from the adaptive model. Training samples for each ternary 
are overlaid. 
Fig. 7. Kou cracking criteria for the four ternaries calculated from 
grid sampling. 
Fig. 8. Relative error ε (equation (22) of the adaptive model compared to the 
grid sampling of the Kou cracking criteria. 
N. Ury et al.                                                                                                                                                                                                                                     
Computational Materials Science 244 (2024 ) 113172 
8 


whereas the cross-validation used during model fitting only considered 
the last five compositions added to the model. The number of samples 
for each binary, ternary, and quaternary system used for the adaptive 
model and grid sampling is shown in Table 2, showing that the number 
of samples required to fit the adaptive model was approximately 3–100 
times lower than for grid sampling, with a smaller percentage of samples 
being needed as the number of components increases. 
Fig. 9 shows a quaternary diagram of the cracking index over the four 
elements calculated from the surrogate model for Kou cracking criteria. 
The cracking index predicts that cracking susceptibility will be highest 
in the Mo-Ta-Ti ternary at around 10–20 at.% Ti and 30–60 at.% Ta 
(balance Mo). Cracking susceptibility is lowest throughout the compo­
sition space in the Mo-Nb-Ta ternary (Fig. 6). Comparing each Ti-X bi­
nary, the maximum cracking susceptibility is lowest in the Ti-Nb binary 
while it is the highest in the Ti-Ta binary. The cracking index calculated 
using the surrogate models for the iCSC and sRDG criteria show similar 
behavior. 
3.2. Path planning in the Mo-Nb-Ta-Ti system 
Three different paths were created using the path planner going from 
Ti-30Mo to pure Ta. The first path (A) considered the three cracking 
criteria (using equation (5)) and path length (equation (1)) as the cost 
function. The three cracking criteria were normalized to be between 
0 and 1. For use in equation (5), the derivatives of these functions were 
added with a weight of 1 for each criterion. The summed cost from 
equation (5) was combined with the path length cost function having a 
weight of 0.1 and the cracking criteria cost function having a weight of 1 
to prevent the path length from having too large of an influence on the 
final path. The second path (B) considered the same cost function; 
however, an obstacle was added for compositions to avoid the formation 
of the HCP phase at 600 ◦C. The third path (C) was the same as the 
second path with the obstacle set to avoid HCP phase formation at 
700 ◦C. Creating the obstacle model for paths B and C was done by 
taking the phase classifier model described earlier and fixing the tem­
perature to 600 or 700 ◦C. 
For the PRM phase of the path planning, batches of 1000 randomly 
generated compositions were added per batch with a search radius for 
nearby compositions set to 0.1, where the existence of a path would be 
checked between batches. This was done until a path was found between 
the initial and final composition. The RRT*FN phase was performed 
with 5000 iterations, where an iteration was counted if a generated 
composition was successfully added to the path tree. The search radius 
for a newly generated composition to any node on the path tree was set 
to 0.2. 
The optimized paths A, B, and C are shown in Fig. 10 with the 
average of the normalized cracking indices and the phase classifier 
model (for paths B and C) overlaid. The compositions and the normal­
ized cracking criteria along the gradient are shown in Fig. 11. For path 
A, the path that would result in the lowest cracking index would be to go 
through the Ti-Nb binary. Considering this, the optimized path resulted 
in going from Ti-30Mo to an Nb-rich composition, then finally going to 
pure Ta. All three cracking susceptibility criteria peak at around 0.4 of 
the path length (shaded region), which corresponds to around a Nb-20Ti 
composition. At this composition, the cracking indices peak at around 
0.4–0.5 of the maximum value for each criterion. The cracking suscep­
tibility drops back down as the path travels to the pure Ta composition. 
The path slightly deviates towards Mo before going to pure Ta. From 
both the surrogate model and the grid sampling of the Kou’s cracking 
index for the Mo-Nb-Ta system (Fig. 6 and Fig. 7), the cracking sus­
ceptibility slightly drops if the a path from Nb to Ta were to go towards 
the Mo corner. 
For path B, the obstacle model avoiding the HCP phase at 600 ◦C 
would prevent the path from going through the Ti-Nb binary as it did in 
path A. The path therefore goes from Ti-30Mo to a Mo-rich composition 
before going to pure Ta. The cracking susceptibility peaks around 0.25 of 
the path length at a value of 0.5–0.6 of the maximum cracking suscep­
tibility for the three criteria (shaded region). This corresponds to around 
Table 2 
Comparison of the number of points used for each binary, ternary and quar­
ternary system using the adaptive surrogate model for Kou’s, iCSC and sRDG 
cracking criteria and the number of samples used for grid sampling.   
Kou’s 
iCSC 
sRDG 
Grid 
Mo-Nb 
17 
17 
12 
51 
Mo-Ta 
17 
12 
22 
51 
Mo-Ti 
12 
12 
12 
51 
Nb-Ta 
17 
12 
17 
51 
Nb-Ti 
12 
12 
17 
51 
Ta-Ti 
22 
22 
17 
51 
Mo-Nb-Ta 
68 
53 
73 
1,326 
Mo-Nb-Ti 
78 
63 
53 
1,326 
Mo-Ta-Ti 
108 
98 
98 
1,326 
Nb-Ta-Ti 
88 
68 
88 
1,326 
Mo-Nb-Ta-Ti 
299 
239 
264 
23,426  
Fig. 9. Contour plot of Kou cracking index on the Mo-Nb-Ta-Ti quaternary system.  
N. Ury et al.                                                                                                                                                                                                                                     
Computational Materials Science 244 (2024 ) 113172 
9 


a Ti-60Mo composition. It is noted that the path appears to oscillate a bit 
in the last half of the path, where the composition of Nb varies between 
0–0.1. It is possible that optimization becomes difficult as the path ap­
proaches a binary system as it would rely on sampled compositions 
being generated closer to the binary, which represents a small volume of 
the quaternary space (even when biasing the sampled compositions to 
be near the current optimal path). 
In path C, the obstacle model would allow the path to reach an Nb- 
rich composition similar to path A. The cracking susceptibility in the 
resulting path peaks at around 0.35 of the path length with a value 
0.4–0.5 of the maximum cracking susceptibility for the three criteria 
(shaded region). This corresponded to a composition of around Nb-20Ti, 
which is similar to the composition in path A where the cracking sus­
ceptibility peaked. As with path A, the region of the path from the Nb- 
rich composition to Ta appears to go towards the Mo-rich corner 
before going to pure Ta. This can be explained using the same reason for 
path A where the cracking susceptibility in the Mo-Nb-Ta ternary rea­
ches a lower value if the path were to deviate towards the Mo-rich region 
compared to the Nb-Ta binary. Despite the cost functions favoring a 
shorter path (from both the path length and the cracking criteria cost 
Fig. 10. Optimized paths A (no obstacles), B (avoid HCP phase at 600 ◦C) and C (avoid HCP phase at 700 ◦C). Plots a), b) and d) show the path plotted against the 
contours of the weighted average of the Kou, iCSC and sRDG cracking criteria. Plots c) and e) show the path plotted against the HCP obstacle function for 600 and 
700 ◦C respectively. Note that the plots are rotated to for clarity. 
N. Ury et al.                                                                                                                                                                                                                                     
Computational Materials Science 244 (2024 ) 113172 
10 


functions), it is possible that the improvement in the cost function due to 
shortening the path from Nb to Ta is small, making optimization diffi­
cult. This is likely what created the difference between path A and C 
where both paths are near optimal, but further optimization becomes 
extremely slow. In addition, as with path B, it is likely that optimization 
is also difficult in the Mo-Nb-Ta ternary space as the probability of 
sampling in the quaternary space is higher. One likely improvement for 
these behaviors is to force the path planner to generate a portion of the 
samples on the binaries and ternaries. This could increase the proba­
bility that a candidate composition could improve the path if the path 
must travel along a binary or a ternary. This procedure could also extend 
to higher ordered systems. For example, for 5-component systems, a 
portion of the samples would be generated on the quaternaries, ter­
naries, and binaries. 
While the path planning approach developed in this work can be 
conducted in high component space and with a generalized set of 
properties, more improvements can be made to increase the perfor­
mance of the path planner as well as incorporating higher fidelity sur­
rogate models. Both the probabilistic road map and rapidly-exploring 
random trees algorithms are stochastic. When path planning for more 
complex alloys, the sampling density in higher dimensional space be­
comes sparser, leading to inefficient sampling as many samples will not 
contribute to further optimizing the path. These samples may be too far 
from the current optimal path, inside an infeasible composition where 
detrimental phases can form, or in a position that will not reduce the cost 
of the current path. It may be possible to sample the composition space 
while accounting for the current path, obstacles, and cost functions. For 
example, while this work implemented sampling near the current path 
Fig. 11. Left) compositions across the optimized path and right) computed cracking indices along the path for optimization on no obstacles, avoiding HCP at 600 ◦C 
and avoiding HCP at 700 ◦C. The shaded regions highlight where the cracking indices are the highest. 
N. Ury et al.                                                                                                                                                                                                                                     
Computational Materials Science 244 (2024 ) 113172 
11 


during the RRT stage of the path planning process, samples may also be 
generated outside of obstacles rather than through rejection sampling. 
Knowledge of the sensitivity of the path to the cost functions may also be 
used to bias the sampling towards a side of the path that will lower the 
total cost. In addition, sampling of lower-component systems in the 
composition space may be beneficial for cases where the optimal path 
lies in these regions. Both the PRM and the RRT algorithm may also be 
improved by parallelization to assess multiple candidate compositions 
synchronously or by binning the composition space to reduce the 
number of distance comparisons between generated compositions. 
Other improvements can be made to the phase classifier and surro­
gate models to improve their fidelity. Using a support vector machine for 
the phase classifier model makes it difficult to reproduce the potentially 
sharp boundaries where a phase may be stable. Different machine 
learning or surrogate models may be used to better reproduce the sharp 
boundaries. The same can be applied for the adaptive surrogate model 
for property prediction. The cracking susceptibility models assessed in 
the Mo-Nb-Ta-Ti systems were smooth; however, smoothness may not 
be guaranteed in systems with intermetallics or complex liquidus sur­
faces. Using radial basis interpolation with a cubic basis function would 
not allow for fitting to non-smooth functions. For future studies, it may 
be useful to investigate other basis functions or even different interpo­
lation techniques that can correctly assess non-smooth functions. 
4. Conclusions 
Designing FGM composition pathways between two dissimilar ma­
terials is complex due to potential incompatibilities between the two 
materials including formation of detrimental phases, sharp changes in 
properties, and high susceptibility to cracking. Effective gradient design 
may require knowledge of these properties in high dimensional space. A 
path planning algorithm was developed combining both PRM and 
RRT*FN and mitigating the disadvantages of each algorithm. A new 
phase classification model was constructed that takes advantage of 
phase equilibria information to reduce the number of samples required 
for fitting. An adaptive sampling scheme was used for creating surrogate 
property models. These were then used in a case study on the Mo-Nb-Ta- 
Ti system to show the flexibility of the path planning algorithm in 
combining different cost functions and phase obstacles. Being able to 
build surrogate models for phase stability and alloy properties as well as 
quickly iterate path planning with different problem setups can result in 
faster FGM designs and aid in experimental design. By improving the 
surrogate models and sampling methods, it would be possible to utilize 
computational path planning on more complex alloys. 
CRediT authorship contribution statement 
Nicholas Ury: Writing – original draft, Visualization, Validation, 
Software, Methodology. Brandon Bocklund: Writing – review & edit­
ing, Software, Methodology, Conceptualization. Aurelien Perron: 
Writing – review & editing, Supervision, Resources, Conceptualization. 
Kaila M. Bertsch: Writing – review & editing, Supervision, Resources, 
Project administration, Funding acquisition, Conceptualization. 
Declaration of competing interest 
The authors declare that they have no known competing financial 
interests or personal relationships that could have appeared to influence 
the work reported in this paper. 
Data availability 
Data in the present study may be provided upon request to the cor­
responding author. 
Acknowledgements 
This work was performed under the auspices of the U.S. Department 
of Energy by Lawrence Livermore National Laboratory under contract 
DE-AC52-07NA27344 and was supported by the LLNL Laboratory 
Directed Research and Development (LDRD) program under project 
tracking code 23-ERD-034. Lawrence Livermore National Security, LLC. 
References 
[1] A. Reichardt, et al., Advances in additive manufacturing of metal-based 
functionally graded materials, Int. Mater. Rev. 66 (1) (2021) 1–29, https://doi.org/ 
10.1080/09506608.2019.1709354. 
[2] L. Yan, Y. Chen, F. Liou, Additive manufacturing of functionally graded metallic 
materials using laser metal deposition, Addit. Manuf. 31 (2020) 100901, https:// 
doi.org/10.1016/j.addma.2019.100901. 
[3] C. Zhang, et al., Additive manufacturing of functionally graded materials: A review, 
Mater. Sci. Eng. A 764 (2019) 138209, https://doi.org/10.1016/j. 
msea.2019.138209. 
[4] J.S. Zuback, T.A. Palmer, T. DebRoy, Additive manufacturing of functionally 
graded transition joints between ferritic and austenitic alloys, J. Alloy. Compd. 770 
(2019) 995–1003, https://doi.org/10.1016/j.jallcom.2018.08.197. 
[5] M.K. Samal, M. Seidenfuss, E. Roos, K. Balani, Investigation of failure behavior of 
ferritic–austenitic type of dissimilar steel welded joints, Eng. Fail. Anal. 18 (3) 
(2011) 999–1008, https://doi.org/10.1016/j.engfailanal.2010.12.011. 
[6] H.T. Wang, G.Z. Wang, F.Z. Xuan, S.T. Tu, Fracture mechanism of a dissimilar 
metal welded joint in nuclear power plant, Eng. Fail. Anal. 28 (2013) 134–148, 
https://doi.org/10.1016/j.engfailanal.2012.10.005. 
[7] M. Rieth, et al., Recent progress in research on tungsten materials for nuclear 
fusion applications in Europe, J. Nucl. Mater. 432 (1–3) (2013) 482–500, https:// 
doi.org/10.1016/j.jnucmat.2012.08.018. 
[8] C. Tan, K. Zhou, T. Kuang, Selective laser melting of tungsten-copper functionally 
graded material, Mater. Lett. 237 (2019) 328–331, https://doi.org/10.1016/j. 
matlet.2018.11.127. 
[9] L. Alacoque, R.T. Watkins, A.Y. Tamijani, Stress-based and robust topology 
optimization for thermoelastic multi-material periodic microstructures, Comput. 
Methods Appl. Mech. Eng. 379 (2021) 113749, https://doi.org/10.1016/j. 
cma.2021.113749. 
[10] A. Ben-Artzy, et al., Compositionally graded SS316 to C300 Maraging steel using 
additive manufacturing, Mater. Des. 201 (2021) 109500, https://doi.org/10.1016/ 
j.matdes.2021.109500. 
[11] S. Firdosy, et al., Compositionally graded joints between magnetically dissimilar 
alloys achieved through directed energy deposition, Scr. Mater. 202 (2021) 
114005, https://doi.org/10.1016/j.scriptamat.2021.114005. 
[12] D.C. Hofmann, et al., Developing gradient metal alloys through radial deposition 
additive manufacturing, Sci Rep 4 (1) (2014) 5357, https://doi.org/10.1038/ 
srep05357. 
[13] L.D. Bobbio, et al., Additive manufacturing of a functionally graded material from 
Ti-6Al-4V to Invar: experimental characterization and thermodynamic 
calculations, Acta Mater. 127 (2017) 133–142, https://doi.org/10.1016/j. 
actamat.2016.12.070. 
[14] A. Reichardt, et al., Development and characterization of Ti-6Al-4V to 304L 
stainless steel gradient components fabricated with laser deposition additive 
manufacturing, Mater. Des. 104 (2016) 404–413, https://doi.org/10.1016/j. 
matdes.2016.05.016. 
[15] L.D. Bobbio, et al., Characterization of a functionally graded material of Ti-6Al-4V 
to 304L stainless steel with an intermediate V section, J. Alloy. Compd. 742 (2018) 
1031–1036, https://doi.org/10.1016/j.jallcom.2018.01.156. 
[16] L.D. Bobbio, et al., Design of an additively manufactured functionally graded 
material of 316 stainless steel and Ti-6Al-4V with Ni-20Cr, Cr, and V intermediate 
compositions, Addit. Manuf. 51 (2022) 102649, https://doi.org/10.1016/j. 
addma.2022.102649. 
[17] E.S. Kim, et al., Local composition detouring for defect-free compositionally graded 
materials in additive manufacturing, Materials Research Letters 11 (7) (2023) 
586–594, https://doi.org/10.1080/21663831.2023.2192244. 
[18] G.H. Gulliver, The quantitative effect of rapid cooling upon the constitution of 
binary alloys, J. Inst. Met. 9 (1) (1913) 120. 
[19] E. Scheil, “Bemerkungen zur Schichtkristallbildung,” International Journal of 
Materials Research, doi: 10.1515/ijmr-1942-340303. 
[20] B. Bocklund, L.D. Bobbio, R.A. Otis, A.M. Beese, Z.-K. Liu, Experimental validation 
of Scheil-Gulliver simulations for gradient path planning in additively 
manufactured functionally graded materials, Materialia 11 (2020) 100689, 
https://doi.org/10.1016/j.mtla.2020.100689. 
[21] B. Dovgyy, M. Simonelli, M.-S. Pham, Alloy design against the solidification 
cracking in fusion additive manufacturing: an application to a FeCrAl alloy, Mater. 
Res. Lett. 9 (8) (2021) 350–357, https://doi.org/10.1080/ 
21663831.2021.1922945. 
[22] S. Kou, A criterion for cracking during solidification, Acta Mater. 88 (2015) 
366–374, https://doi.org/10.1016/j.actamat.2015.01.034. 
[23] M.A. Easton, M.A. Gibson, S. Zhu, T.B. Abbott, An A priori hot-tearing indicator 
applied to die-cast magnesium-rare earth alloys, Metall Mater Trans A 45 (8) 
(2014) 3586–3595, https://doi.org/10.1007/s11661-014-2272-7. 
[24] T.W. Clyne, G.J. Davies, A new hot-tearing criterion, Br. Foundrym 74 (1981) 65. 
N. Ury et al.                                                                                                                                                                                                                                     
Computational Materials Science 244 (2024 ) 113172 
12 


[25] Z. Yang, H. Sun, Z.-K. Liu, A.M. Beese, Design methodology for functionally graded 
materials: Framework for considering cracking, Addit. Manuf. 73 (2023) 103672, 
https://doi.org/10.1016/j.addma.2023.103672. 
[26] T. Kirk, E. Galvan, R. Malak, R. Arroyave, Computational design of gradient paths 
in additively manufactured functionally graded materials, J. Mech. Des. 140 (11) 
(2018) 111410, https://doi.org/10.1115/1.4040816. 
[27] O.V. Eliseeva, et al., Functionally graded materials through robotics-inspired path 
planning, Mater. Des. 182 (2019) 107975, https://doi.org/10.1016/j. 
matdes.2019.107975. 
[28] T. Kirk, R. Malak, R. Arroyave, Computational design of compositionally graded 
alloys for property monotonicity, J. Mech. Des. 143 (3) (2021) 031704, https:// 
doi.org/10.1115/1.4048627. 
[29] E. Galvan, R.J. Malak, S. Gibbons, R. Arroyave, A constraint satisfaction algorithm 
for the generalized inverse phase stability problem, J. Mech. Des. 139 (1) (2017) 
011401, https://doi.org/10.1115/1.4034581. 
[30] A. Abu-Odeh, et al., Efficient exploration of the high entropy alloy composition- 
phase space, Acta Mater. 152 (2018) 41–57, https://doi.org/10.1016/j. 
actamat.2018.04.012. 
[31] F. Pedregosa, et al., Scikit-learn: machine learning in python, J. Mach. Learn. Res. 
12 (2011) 2825–2830. 
[32] C. Kamath, Data mining and statistical inference in selective laser melting, Int J 
Adv Manuf Technol 86 (5–8) (2016) 1659–1677, https://doi.org/10.1007/s00170- 
015-8289-2. 
[33] D. P. Mitchell, “Spectrally optimal sampling for distribution ray tracing,” Computer 
Graphics, vol. 25, no. 4, 1991, doi: 10.1145/122718.122736. 
[34] T.J. Mackman, C.B. Allen, M. Ghoreyshi, K.J. Badcock, Comparison of adaptive 
sampling methods for generation of surrogate aerodynamic models, AIAA J. 51 (4) 
(2013) 797–808, https://doi.org/10.2514/1.J051607. 
[35] G. E. Fasshauer, Meshfree approximation methods with matlab, vol. 6. in 
Interdisciplinary Mathematical Sciences, vol. 6. WORLD SCIENTIFIC, 2007. doi: 
10.1142/6453. 
[36] J.N. Fuhg, A. Fau, U. Nackenhorst, State-of-the-art and comparative review of 
adaptive sampling methods for kriging, Arch Computat Methods Eng 28 (4) (2021) 
2689–2747, https://doi.org/10.1007/s11831-020-09474-6. 
[37] H. Liu, J. Cai, Y.-S. Ong, An adaptive sampling approach for Kriging metamodeling 
by maximizing expected prediction error, Comput. Chem. Eng. 106 (2017) 
171–182, https://doi.org/10.1016/j.compchemeng.2017.05.025. 
[38] T.H. Cormen, C.E. Leiserson, R.L. Rivest, S. Clifford, Introduction to Algorithms, 1st 
ed., MIT Press and McGraw-Hill, 1990. 
[39] L.E. Kavraki, P. Svestka, J.-C. Latombe, M.H. Overmars, Probabilistic roadmaps for 
path planning in high-dimensional configuration spaces, IEEE Trans. Robot. 
Automat. 12 (4) (1996) 566–580, https://doi.org/10.1109/70.508439. 
[40] L.E. Kavraki, M.N. Kolountzakis, J.-C. Latombe, Analysis of probabilistic roadmaps 
for path planning, IEEE Trans. Robot. Automat. 14 (1) (1998) 166–171, https:// 
doi.org/10.1109/70.660866. 
[41] M.L. Fredman, R.E. Tarjan, Fibonacci heaps and their uses in improved network 
optimization algorithms, J. Association for Computing Machinery 34 (3) (1987) 
596–615. 
[42] S.M. LaValle J.J. Kuffner Randomized kinodynamic planning Inte. J. Robotics Res. 
20 5 378 400 10.1177/02783640122067453. 
[43] S. Karaman, E. Frazzoli, Sampling-based algorithms for optimal motion planning, 
Int. J. Robotics Res. 30 (7) (2011) 846, https://doi.org/10.1177/ 
0278364911406761. 
[44] O. Adiyatov and H. A. Varol, “Rapidly-exploring random tree based memory 
efficient motion planning,” in 2013 IEEE International Conference on Mechatronics 
and Automation, Takamatsu, Kagawa, Japan: IEEE, Aug. 2013, pp. 354–359. doi: 
10.1109/ICMA.2013.6617944. 
[45] B. Li, B. Chen, An Adaptive rapidly-exploring random tree, IEEE/CAA J. Autom. 
Sinica 9 (2) (2022) 283–294, https://doi.org/10.1109/JAS.2021.1004252. 
[46] R. Otis, Z.-K. Liu, pycalphad: CALPHAD-based computational thermodyamics in 
Python, J. Open Res. Software 5 (1) (2017) 1, https://doi.org/10.5334/jors.140. 
[47] B. Bocklund, L. D. Bobbio, R. Otis, A. M. Beese, and Z.-K. Liu, “pycalphad-scheil: 
0.1.2,” 2020, doi: 10.5281/zenodo.3630657. 
[48] I. Ansara, A.T. Dinsdale, M.H. Rand, European, Definition of thermochemical and 
thermophysical properties to provide a database for the development of new light 
alloys: Thermochemical database for light metal alloys, Communities 3 (1998) 3. 
[49] W. Xiong, et al., Thermodynamic assessment of the Mo–Nb–Ta system, Calphad 28 
(2) (2004) 133–140, https://doi.org/10.1016/j.calphad.2004.07.002. 
[50] Y. Zhang, H. Liu, Z. Jin, Thermodynamic assessment of the Nb-Ti system, Calphad 
25 (2) (2001) 305–317, https://doi.org/10.1016/S0364-5916(01)00051-7. 
[51] F.H. Cocks, R.M. Rose, J. Wulff, Segregation of tantalum at very low concentrations 
in niobium by controlled solidification: a neutron-activation study, J. Less 
Common Metals 10 (3) (1966) 157–168, https://doi.org/10.1016/0022-5088(66) 
90107-X. 
[52] A.L. Gavzeo, P.B. Budberg, S.A. Minayeva, Construction of the solidus diagram for 
the Ti-Ta-Nb system using the method of mathematical statistics, Russ. Metall. 
(1969). 
[53] N.N. Sobolev, V.I. Levanov, O.P. Elyutin, V.S. Mikheyev, The construction of 
fusibility diagrams for the Ti-V-Nb-Mo system by the simple lattice method, Russ. 
Metall. (1974). 
N. Ury et al.                                                                                                                                                                                                                                     
Computational Materials Science 244 (2024 ) 113172 
13 



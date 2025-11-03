The printing of metals is the fastest growing sector1 of 
additive manufacturing (AM) because of its capability 
to manufacture parts that cannot be made by other pro-
cesses, soon after their design, while minimizing the 
number of processing steps1–4. In the printing of metals, 
the 3D design of a part is combined with manufactur-
ing software to produce a solid metallic part. Parts are 
made in a layer-​by-​layer manner and using various heat 
sources and feedstocks. Aerospace, healthcare, energy, 
automotive, marine and consumer product indus-
tries all use printed metallic parts2. Examples of such 
parts include patient-​specific metal implants5, turbine 
blades with internal cooling channels6, manifolds for 
engines and turbines, and lattice structures and truss 
networks with optimized strength to weight ratios7. 
Many parts that previously required assembly can now 
be printed as a single unit3. AM is also capable of fab-
ricating parts with site-​specific chemical compositions 
and properties8.
The major variants of metal printing1–3, either directed 
energy deposition (DED) or powder bed fusion (PBF), 
differ by the type of feedstock (powder or wire) and the 
heat source, either laser (L), electron beam (EB), plasma 
arc (PA) or gas metal arc (GMA) (Fig. 1). With the aid of 
computers, the motion of these heat sources is guided by 
a digital definition of the part, which results in the melt-
ing of metals, in a layer-​by-​layer manner, to construct 
3D objects1. A focused laser or electron beam then selec-
tively scans the surface and melts the powder particles 
into the desired shape for each successive layer, until the 
3D part is printed3. By using very small diameter beams 
and tiny metal particles, intricate parts with fine and 
closely spaced features are printed. In DED, a powder or 
wire is supplied from above the build, whereas in PBF 
thin layers of powder, often thinner than human hair, 
are added after each layer is fused. These metal printing 
processes also differ in their heat source power, scanning 
speed, deposition rate, build size and other important 
attributes3 (Table 1). The data show that the scanning 
speed and power vary widely depending on the spe-
cific process used. These variations result in an extreme 
10,000-​fold difference of the cooling rates, as well as vast 
differences in temperature gradient and heat input, not 
encountered in conventional materials processing9. The 
cooling rate and heat input affect the microstructure 
and properties of components, and, hence, these param-
eters must be controlled more carefully than those for 
the conventional processes to obtain good quality and 
reliable parts.
In DED, the feedstock, in the form of powder or wire, 
is melted either by a laser, an electron beam or an arc heat 
source. Unlike PBF, most DED processes are not con-
fined by a bed or box of prescribed dimensions, allowing 
large parts to be created1,3,10. Wire-​based DED is closely 
Metallurgy, mechanistic models and 
machine learning in metal printing
T. DebRoy   1 ✉, T. Mukherjee1, H. L. Wei   2, J. W. Elmer   3 and J. O. Milewski   4
Abstract | Additive manufacturing enables the printing of metallic parts, such as customized 
implants for patients, durable single-​crystal parts for use in harsh environments, and the printing 
of parts with site-​specific chemical compositions and properties from 3D designs. However, the 
selection of alloys, printing processes and process variables results in an exceptional diversity of 
microstructures, properties and defects that affect the serviceability of the printed parts. Control 
of these attributes using the rich knowledge base of metallurgy remains a challenge because of 
the complexity of the printing process. Transforming 3D designs created in the virtual world into 
high-​quality products in the physical world needs a new methodology not commonly used in 
traditional manufacturing. Rapidly developing powerful digital tools such as mechanistic models 
and machine learning, when combined with the knowledge base of metallurgy, have the potential 
to shape the future of metal printing. Starting from product design to process planning and 
process monitoring and control, these tools can help improve microstructure and properties, 
mitigate defects, automate part inspection and accelerate part qualification. Here, we examine 
advances in metal printing focusing on metallurgy, as well as the use of mechanistic models and 
machine learning and the role they play in the expansion of the additive manufacturing of metals.
1Department of Materials 
Science and Engineering,  
The Pennsylvania State 
University, University Park, 
PA, USA.
2School of Mechanical 
Engineering, Nanjing 
University of Science and 
Technology, Nanjing, China.
3Materials Engineering 
Division, Lawrence Livermore 
National Laboratory, 
Livermore, CA, USA.
4APEX3D LLC, Santa Fe,  
NM, USA.
✉e-​mail: debroy@psu.edu
https://doi.org/10.1038/ 
s41578-020-00236-1
REVIEWS
www.nature.com/natrevmats
48 | January 2021 | volume 6	


related to conventional welding processes, and uses high 
powers to produce thick layers at high deposition rates to 
manufacture large parts economically4. Parts produced 
by DED-​GMA, DED-​PA and DED-​L typically require 
machining owing to the high degree of surface waviness 
that results from large molten pools1. The exterior of a 
wavy part resembles the surface of a lake on a windy 
day with crests and troughs that scale with the AM layer 
height, which is smaller than the molten pool size. The 
electron beam processes are performed in a vacuum or 
in inert gas of low pressure allowing the processing of 
reactive metals, whereas the other heat sources require 
shielding of the parts using an inert gas1. Some AM 
processes do not require the melting of the feedstock. 
Instead, thin sheets and ribbons of metallic materials 
are consolidated by ultrasonic methods1–3. Alloy pow-
ders are also bound together by jetting a binder in a 
powder bed and then sintering in a high-​temperature 
furnace3.
AM processes have a large number of parameters, 
including the power and speed of the heat source, 
power density, feedstock geometry, delivery method 
and scanning pattern9. Parameter selection is impor-
tant because it affects the shape and size of the molten 
pool, and the resulting thermal cycles, cooling rates, 
temperature gradients and solidification rates, which in 
turn determine the evolution of microstructure, defects 
and properties1. However, straightforward control of 
the microstructure, defects and properties remains 
elusive2 because of the need to conduct many experi-
ments to explore a large range of process parameters. 
The printing conditions are often selected based on the 
recommendations of the machine manufacturer or by 
trial and error11. Predictions of microstructures, prop-
erties and defects in printed parts require both theo-
ries of metallurgy and knowledge of how AM process 
parameters affect these features. However, metallurgical 
principles cannot predict the process variables needed 
to achieve good microstructures and mechanical prop-
erties. Mechanistic models and machine learning can 
provide the connection between process variables, part 
geometry, composition, microstructure, mechanical 
properties and defects for a given alloy. Such correlations 
are important because they can reduce the number of 
experiments needed to achieve high-​quality parts.
Improving part quality by trial and error is not opti-
mum for AM because of the high costs of feedstock and 
machines9 combined with a changing economic culture 
where new products are rapidly created. Mechanistic 
models can predict physical attributes such as the tem-
perature and velocity fields, microstructure and defect 
formation based on process variables, and thermo-
physical properties of alloys using phenomenological 
understanding12. If this understanding is lacking but 
data are available on process variables, alloy properties 
and product attributes, then machine learning13 can 
make valuable contributions to the quality of printed 
parts. Starting from part design, process planning, 
process monitoring and control, machine learning can 
help reduce defects, achieve superior microstructures 
and properties, and facilitate product quality inspec-
tion for accelerated product qualification. The rapidly 
developing mechanistic models and machine learning 
algorithms can also open opportunities for printing 
new alloys9. The synergistic applications of metallurgy, 
mechanistic models and machine learning are impor-
tant for the design, process planning, production, 
characterization and performance evaluation of printed 
parts (Fig. 2).
Metallurgy
Metallurgy has a mature knowledge base of processing, 
microstructure, properties and performance. Yet there 
are several issues of metal printing that cannot be under-
stood using this knowledge. Printing of single crystals, 
parts with site-​specific properties, superior combina-
tions of properties not easily attainable by other man-
ufacturing processes, unique metal matrix composites 
and parts with tailored solidification morphology and 
texture is complex and requires expansion of the existing 
knowledge base of metallurgy.
Printing single-​crystal parts
AM layers are connected to the previous layer through 
melting, solidification and epitaxial growth, which 
creates metallurgical texture in the part. Texture may 
Laser beam
Mirror
Roll
Substrate
Powder
added
Moves down to 
allow deposition 
of new layer
Powder
bed
Powder
spreader
Gas metal arc
Deposition of metal
on substrate
Arc
Consumable wire 
Directed energy deposition
using gas metal arc and wire
Powder bed fusion with
laser heat source
Powder
Deposition of metal
on substrate
Powder
feeding nozzle
Coaxial 
laser beam
Directed energy deposition
using laser and powder
Fig. 1 | Schematics of three metal printing processes. Powder bed fusion with a laser heat source (left), directed energy 
deposition using a powder and laser heat source (middle) and directed energy deposition with a wire and gas metal arc 
heat source (right). Some important attributes1–3,9,186,187,240 of these processes are shown in Table 1. Cup in right image is 
adapted from ref.240, Springer Nature Limited.
nature Reviews | MAteRiAlS
Reviews
	
 volume 6 | January 2021 | 49


or may not be desirable but can be used advanta-
geously in traditional directionally solidified or single-​ 
crystal parts where superior high-​temperature creep 
resistance is required for aero-​engine turbine parts14. 
AM is now being used in the fabrication and repair of 
single-​crystal parts15,16. PBF and DED processes have 
made single-​crystal, nickel-​based superalloy parts 
using both laser and electron beam heat sources through 
control of solidification parameters14–24. For example, 
a CMSX-4 single-​crystal cylinder 75 mm long and 
12 mm in diameter was printed using PBF-​EB22 (Fig. 3a). 
The larger rupture strain of the heat-​treated single crys-
tal results in slightly longer creep life than conventionally 
processed alloys14.
The most important requirement to print a single- 
crystal part is to maintain an appropriate combination 
of the temperature gradient and solidification growth 
rate to facilitate directional solidification23. These tem-
peratures and growth rates can be achieved by preheating 
the powder bed14,19–22 and using complex combinations 
of scanning pattern and speed18,23. More specifically, high 
power, a low scanning velocity and a moderate powder 
feeding rate were beneficial to fabricate single-​crystal 
parts23. However, the directional solidification of single 
crystals still requires the optimization of some process 
conditions, including the preheat temperature, heat 
input and scanning strategy25. Well-​tested mechanistic 
models of AM processes26 can calculate the temperature 
gradients and the solidification growth rates based on 
which the conditions for directional solidification can 
be determined.
A common difficulty in printing single-​crystal parts 
is the formation of stray grains. These grains18,25 form 
primarily near the top edge of the deposit owing to 
high convective and radiative heat losses from the top 
surface of the molten pool that disrupts directional 
solidification. Stray grains are not observed in the inte-
rior layers because of their remelting. The regions with 
stray grains can be removed by machining. A quantita-
tive understanding of printing single crystals is evolving. 
Developing high-​fidelity mechanistic models of direc-
tional solidification in AM parts and databased machine 
learning need more work.
Site-​specific properties
Parts such as gears and crankshafts require hard surfaces 
and soft cores, and AM enables the printing of such parts 
with site-​specific properties. For a single-​alloy part, 
site-​specific properties can be achieved by tailoring the 
microstructure by controlling heat input and scanning 
strategies in both DED and PBF8,27. Varying grain size 
and tensile properties are achieved in an stainless steel 
316 (SS 316) part printed using PBF-​L by adjusting both 
the laser power and the scanning pattern28.
In the functionally graded parts, site-​specific proper-
ties can be achieved by varying the chemical composition 
and microstructure of parts over the desired distance. 
DED29,30, PBF31 and an AM process combining wire and 
powder32 have been used to produce graded alloys. The 
compositional variation in a graded joint between ferri-
tic 2.25Cr–1Mo steel and austenitic alloy 800H can be 
produced by DED-​L (Fig. 3b). Such joints are useful for 
nuclear reactors but suffer from creep degradation at ele-
vated temperatures because of the diffusive loss of carbon. 
The graded joint, when placed in service at 1,073 K, can 
significantly reduce carbon depletion by diffusion across 
the joint compared with joints between dissimilar alloys 
(Fig. 3b). As a result, a significant improvement in creep 
properties is achieved30. Also, a graded part between SS 
304L and nickel alloy, Invar 36, was printed using DED-L 
to achieve a low coefficient of thermal expansion without 
sacrificing the strength and toughness of the part33.
Table 1 | Comparison of various parameters and attributes of three metal printing processes
Parameter or process
Powder bed fusion with  
a laser or electron beam
Directed energy 
deposition using  
a powder and laser
Directed energy deposition 
using a wire (electron beam, 
plasma arc or gas metal arc)
Heat source power3 (W)
50–1,000 (up to 4 beams)
400–3,000
1,000–5,000 (gas metal arc 
2,000)
Scanning speed1–3 (mm s–1)
10–1,000
6–60
5–50
Deposition rate3,186 (cm3 h–1)
25–180
20–450
100 to >1,000
Build size (mm × mm × mm)
Maximum 800 × 400 × 500
Maximum 2,000 × 
1,500 × 1,000
Maximum 5,000 × 3,000 × 1,000
Feedstock diameter (µm)
15–60 (laser), 45–105 
(electron beam)
15–105
900–3,000
Dimensional accuracy186,187 (mm)
0.04–0.20
0.20–5
1–5
Surface roughness1–3 (average 
deviation of surface from  
its mean height in µm)
7–30 (laser), 20–50  
(electron beam)
15–60
45–200+, surface needs 
machining
Post processing
Heat treatment, hot isostatic 
pressing, machining
Heat treatment, 
machining, grinding
Heat treatment, stress 
relieving, machining
Cooling rate during 
solidification1–3,9 (K s–1)
105–107
102–104
101–102
Temperature gradient1–3,9 (K m–1)
106–107
105–106
103–104
Solidification growth rate1–3,9 
(m s–1)
10–1–100
10–2–10–1
10–2–10–1
www.nature.com/natrevmats
Reviews
50 | January 2021 | volume 6	


The AM of materials with site-​specific properties 
is often challenging because of defects. For example, 
a graded part between Ti–6Al–4V to Invar 36 can fail34 
because of the formation of brittle intermetallic phases 
including FeTi, Fe2Ti, Ni3Ti and NiTi2 in the gradient 
region. Unwanted phases are known to degrade the 
mechanical properties of parts29,35. Machine learning, 
combined with the metallurgical knowledge, has been 
used to find the optimum process parameters to avoid 
the formation of brittle phases36.
Unique combination of properties
Combinations of superior properties of printed parts, 
not attainable by conventional manufacturing, have 
been reported. For example, the strength and ductility 
of stainless steel parts were simultaneously enhanced37–41, 
defying the expected strength–ductility trade-​off com-
mon in conventional manufacturing. This unusual 
behaviour has been attributed to hierarchal microstruc-
ture37, dislocation networks that retard but do not pre-
vent dislocation movements37,38, nano-​cellular structure 
in fine grains39, unusual texture and twinning40,41, and 
extremely fine solidification cells41. The presence of 
twinning in SS 316, built by PBF-​L, has been suggested as 
a contributing factor for its ductility (Fig. 3c). In addition, 
the printed part shows increased strength and ductility, 
and a reduction of defects compared with a wrought 
alloy (Fig. 3c).
Improvements in strength without any degrada-
tion of ductility have also been reported in titanium 
alloys42–48, SS 316L (ref.49) and 12CrNi2 (ref.50) and 
Al–12Si (ref.51) alloys. There are several different mech-
anisms for titanium alloys42–48. For example, rapid cool-
ing during PBF-​L of Ti–22Al–25Nb (ref.43) increases 
dislocation density owing to stress accumulation and 
forms a nanoscale hexagonal omega precipitate. Both a 
high dislocation density and precipitates hinder dislo-
cation movement and contribute to the high strength 
without degradation of ductility. During solidification 
of Ti–6Al–4V, columnar grains of a body-​centred cubic 
beta phase form. Subsequently, a hexagonal close-​packed 
alpha phase grows inside the prior beta phase. The small 
sizes of both alpha and beta phases during DED-​PA 
enhance strength44. In addition, heat treatment results 
in a globular shape of the alpha phase, enhancing tough-
ness46. Rapid cooling of Ti–6Al–4V during PBF-​L forms 
hexagonal close-​packed martensite, which enhances 
strength48. Similarly, a fine-​grain microstructure 
with nanoscale precipitates improves the mechanical 
properties of Ti185 alloy (Ti–Al–V–Fe)47.
The aforementioned results are exciting, but the 
improvement in properties of alloys is not realized under 
all processing conditions52. This observation is hardly 
surprising because the cooling rate, temperature gra-
dient and solidification growth rate vary considerably 
for different AM methods and processing conditions, 
Mechanistic models 
Connects process 
variables to product 
attributes via 
mechanistic 
understanding
Metallurgy
Connects process, 
microstructure, 
properties and 
performance
Machine learning
Connects process 
variables to product 
attributes using 
available data
Product design
Part geometry, density, 
support structure, weight, 
build time, feedstock 
selection
Process planning
Process selection, 
optimization of AM 
parameters, geometry, 
microstructure, properties
Production, monitoring 
and control
Melt pool data, spatter, 
defect detection, machine 
condition, process control
Properties
Composition, tensile, 
fatigue, creep, corrosion 
resistance, anisotropy
Inspection
Melt pool features, 
spatter, defect detection, 
machine conditions, 
dimensional tolerance
Performance
Serviceability, lifetime, cost, 
qualiﬁcation, certiﬁcation
Defects
Porosity, lack of 
fusion, cracking, 
distortion, 
roughness, residual 
stress, waviness
Microstructure
Grain structure, 
solidiﬁcation 
structure, primary and 
secondary phases, 
evolution of texture
Fig. 2 | Contributions of metallurgy, mechanistic models and machine learning in the various steps of metal printing. 
The interrelation between machine learning, mechanistic models and metallurgy is shown by bidirectional black arrows. 
Some variables needed in machine learning, such as temperature, are difficult to measure but can be readily calculated 
using mechanistic models. The process–structure–properties–performance relations in metallurgy are complex and not 
always quantitative. Both mechanistic models and machine learning can provide a quantitative framework to understand 
metallurgical attributes of parts. The contributions of machine learning, metallurgy and mechanistic models in the various 
steps in the production and characterization of parts are shown by the grey, green and sky-​blue lines, respectively.  
AM, additive manufacturing.
nature Reviews | MAteRiAlS
Reviews
	
 volume 6 | January 2021 | 51


and, hence, the parts produced have a wide variety of 
microstructures and properties9. Further studies are 
required to understand the unusual microstructures and 
properties of printed metallic parts and their underlying 
mechanisms.
Composites
AM offers a means to synthesize unique metal matrix 
composites with excellent properties. Improvements in 
microstructure and properties have been observed by 
adding small amounts of non-​metallic particles to the 
feedstock. This addition enables the incorporation of 
insoluble second-​phase particles into the alloy, which 
contributes to mechanical loading or other property 
advantages, or creates second phases in situ to modify 
the base alloy by means of nucleation enhanced grain 
refinement. Examples include, Al, Ti and steel-​based 
metal matrix composites of Al/Fe2O3, AlSi10Mg/SiC, 
Al/ZnO, Ti/C, Ti/SiC, Ti/Si3N4, Ti/Mo2C and Fe/SiC53.
Incorporation of second phases. TiC has been added to 
Inconel 718 (refs54,55) and Inconel 625 (ref.54), and carbon 
nanotubes have been added to Inconel 625. Addition 
of nano-​TiC to Inconel 718 strengthens the alloy54,55 
and reduces the coefficient of friction and wear rate54. 
These benefits have been attributed to a combination 
of three effects: changes in dislocation density owing 
to the residual plastic strain caused by the mismatch of 
thermal expansion between the two phases; the Orowan 
strengthening effect that represents strengthening owing 
to interaction between dislocations and small particles; 
and the Hall–Petch effect54 that indicates higher strength 
10% 800H
20% 800H
30% 800H
70% 800H
90%
40% 800H
80%
60% 800H
50% 800H
Cr
Fe
Ni
Time (h)
Creep strain
AM 
Conventional 
75 mm 
12 mm 
0
10
20
30
40
0
20
40
60
80
100
Number of years of service
% Of the initial
carbon depleted
Dissimilar joint
Graded joint
0
10
20
30
Height (mm)
100
80
60
40
20
0
Composition (wt%)
800H
c  High strength and ductility
2 nm
2 nm
b = 1/2[1 1 0]
Engineering stress (MPa)
Wrought-annealed
Additively manufactured
Engineering strain
700
500
300
100
0.0
0.3
0.6
0.9
d  Composite of Ti–6Al–4V and carbon nanotubes
e  CET Zr nanoparticles in Al 7075, PBF-L 
f  Scanning direction changes texture 
   Inconel 718, DED-L 
Tensile strength (MPa)
1,000
900
800
700
600
Strain at failure (%)
20
16
12
8
4
Tensile strength (MPa)
500
400
300
200
100
0
0
2
4
6
Elongation (%)
Al 7075 + Zr
Al 7075 
CET by Zr addition
Large columnar grains
a  Single crystal of a nickel alloy, CMSX-4
b  Site-speciﬁc properties
Cr–Mn steel
0
50
100
150
200
250
300
350
0.00
0.05
0.10
0.15
0.20
0.25
0.30
0 CNT
0.1 CNT
10 μm
20 μm
0 CNT
0.03 CNT
0.1 CNT
100 μm
100 μm
100% 800H
Strain
at failure
Tensile
strength
0.2% proof
stress 
60°
90°
45°
45°
90°
60°
(001)
(001)
(001)
(100)
(100)
(001)
(001)
(001)
www.nature.com/natrevmats
Reviews
52 | January 2021 | volume 6	


for smaller grain size. When added to Inconel 625, TiC 
changes texture56 and significantly improves microhard-
ness, tensile and wear properties. Small and optimal 
amounts of carbon nanotubes (0.25 wt%) increase both 
strength and ductility owing to grain boundary pinning 
and grain refinement57.
Microstructural modification and grain refinement. 
Addition of TiB2 particulates to AlSi10Mg results in tex-
tureless fine grains (average size 2 μm) and cells (<1 μm) 
with well-​dispersed TiB2 nanoparticles inside the grains 
and rod-​like nano-​Si precipitates inside the cells. Both 
the nano-​Si and TiB2 exhibited highly coherent inter-
faces because of sequential solidification58. Graphene 
oxide in an aluminium matrix noticeably improved the 
mechanical performance of the composite made by PBF-​L 
as a result of Al4C3 nanorods formed in situ by the reac-
tion of Al and graphene oxide59. Addition of carbon 
nanotubes to AlSi10Mg helped to achieve higher den-
sity60 parts compared with parts without carbon nano-
tubes. TiB2 in SS 316 reduced the size of the molten pool 
and disrupted the directional properties49.
The addition of up to 0.1 wt% carbon in Ti–6Al–4V 
improved tensile strength and ductility because of 
the decrease in prior β grain size and α lath length61. The 
addition of carbon forms titanium carbide nanoparticles 
that act as grain refiners. Figure 3d indicates the micro-
structures of Ti–6Al–4V alloy with (left microstructure) 
and without (right microstructure) the addition of 0.1% 
carbon. The resulting strengthening effect owing to the 
refining of microstructures is also observed (Fig. 3d). 
The amount of additives is determined experimentally 
and more studies are needed to optimize the effects of 
carbon addition on the microstructure and properties 
of Ti–6Al–4V. A review of the fabrication, mechanical 
properties and defects in particle-​reinforced nanocom-
posites made by selective laser melting indicates limited 
wettability of the nanoparticle and the tendency of the 
nanoparticles to agglomerate as important problems62.
Columnar to equiaxed transition
The structure of printed alloys is often dominated by 
elongated columnar grains and strong texture63–65 result-
ing in anisotropic properties, degradation of strength 
and the formation of cracks in many alloys66,67. Equiaxed 
grains with equal dimensions in all directions minimize 
crack formation and improve properties58,66,67. From our 
knowledge of welding and metal casting, there are two 
approaches to promote columnar to equiaxed transition 
(CET). The first approach relies on control of the pro-
cessing conditions and alloy composition to generate 
favourable solidification conditions for equiaxed grain 
formation. These conditions consist of a low value for 
the temperature gradient to solidification rate ratio 
(G/R ratio) at the liquid/solid interface, which is the param­
eter that controls undercooling through the well- 
known constitutional supercooling mechanism68. The 
second approach relies on the introduction of small parti-
cles into the feedstock to create nuclei for equiaxed grain 
formation. These particles need to have low solubility 
in the molten pool and are often composed of elements 
with high melting points or non-​metallic compounds.
Controlling the process parameters to promote a CET 
requires understanding that there is a maximum value of 
the G/R ratio for each alloy and there is no universal set 
of parameters favourable for equiaxed grain formation. 
In practice, adjustments of heat source power, scanning 
speed, hatch spacing, layer thickness and scanning strat-
egy are useful to attain low G/R ratios that favour CET 
for each alloy. For example, CET was achieved during 
DED-​L of Al–5Si–1Cu–Mg alloy by adjusting the layer 
thickness69. However, creating process conditions for 
producing low G/R ratios is challenging because the 
temperature gradient and solidification rate cannot be 
directly measured or independently controlled, and 
changes in process parameters can result in defects70,71. 
Solidification maps are available for many common 
alloys that can be helpful to achieve CET72. The chemical 
composition of the alloy can be further altered to restrain 
the growth of the columnar grains68. These methods rely 
on creating conditions that favour a wider range of G/R 
ratios for CET to occur through constitutional super-
cooling during regrowth from the previously deposited 
layers, rather than directly nucleating new grains ahead 
of the liquid/solid interface.
The second method for achieving CET is the addition 
of high melting point metallic or non-​metallic nucle­
ating agents with carefully selected crystallographic pro­
perties58,66,68,73. In this approach, intentionally designed 
low energy-​barrier heterogeneous nucleating agents, 
Fig. 3 | Properties of printed metallic components. a | A single crystal14 of a nickel alloy, 
CMSX-4, fabricated by powder bed fusion using an electron beam (top). The single 
crystal shows superior creep property compared with a conventionally manufactured 
part (bottom). b | Site-​specific properties of a compositionally graded joint between a 
nickel alloy, 800H, and a chromium–manganese steel30 fabricated by directed energy 
deposition using a laser beam (DED-​L). Upper plot shows the variation of chemical 
composition along the build direction. Lower plot shows that the graded component 
significantly reduces the depletion of carbon compared with that from the dissimilar 
joint. c | Both improved strength and ductility can be achieved in a stainless steel part 
fabricated by DED-​L39. Scanning tunnelling electron microscopy micrographs show 
atomic structures of the bunched nano-​twins and twin boundary with a step. The twin 
and matrix are shown in blue and yellow, respectively (top). The magnitude and the 
direction of the lattice distortion (b: Burgers vector) is shown by the white arrow. 
The stress–strain plots of additively manufactured components show superior strength 
and ductility compared with the annealed wrought specimens (bottom). d | A composite 
material consisting of Ti–6Al–4V and carbon nanotubes (CNT) fabricated by directed 
energy deposition using a gas metal arc improves microstructure and mechanical 
properties61 (top). Scanning electron microscopy images show reduction of the α lath 
length owing to the addition of carbon nanotubes. The addition of carbon nano­tubes 
improves the 0.2% proof stress, tensile strength and strain at failure (bottom). e | A columnar 
to equiaxed transition (CET) and an improvement of toughness66 occur on addition of 
zirconium nanoparticles to 7075 aluminium alloy (Al 7075) during powder bed fusion 
with a laser heat source (PBF-​L). As a consequence of zirconium addition, the grain 
morphology changes from columnar (left) to equiaxed (right). The toughness improves 
because of the formation of equiaxed grains (bottom). f | Optical micrographs show 
changes in the direction of crystal growth depending on the scanning direction82 for 
DED-​L of Inconel 718. In the unidirectional scanning pattern, the growth direction of the 
primary dendrites was at an angle of about 60° with the horizontal scanning direction 
(top). If the laser beam is scanned in alternate directions in each layer, then the primary 
dendrites grow in a zig-​zag pattern (bottom). Both modelling (right) and experimental 
(left) results are shown. AM, additive manufacturing. Panel a (top) adapted from REF.22,  
CC BY 4.0. Panel a (bottom) adapted with permission from ref.14, Elsevier. Panel b (top) 
adapted with permission from ref.30, Elsevier. Panel b (bottom) constructed with data  
from ref.30. Panel c adapted with permission from ref.39, Elsevier. Panel d adapted from  
ref.61, Springer Nature Limited. Panel e adapted from ref.66, Springer Nature Limited.  
Panel f adapted from ref.82, Springer Nature Limited.
◀
nature Reviews | MAteRiAlS
Reviews
	
 volume 6 | January 2021 | 53


often nano-​particulate powders, are added to the feed-
stock material in small amounts, at quantities usually less 
than 1% (ref.66). It is also important to generate signifi-
cant constitutional supercooling ahead of the solidifying 
dendrite tip to create conditions for nucleating agents 
to work, and the particles must be of appropriate size 
and chemistry to survive in the molten pool. These con-
ditions require the composition, crystal structure, size 
and physical properties of a given nucleating agent to be 
considered in addition to its thermal surroundings in 
the molten pool in order to produce CET. For example, 
molybdenum, zirconium and La2O3 were added during 
DED-​GMA of Ti–6Al–4V to form equiaxed grains68. 
CET was achieved in PBF-​L of AlSi10Mg alloy by add-
ing nano-​TiB2 (ref.58). A CET was observed by adding 
a small amount of zirconium nanoparticles to 7075 
aluminium alloy and the strength and ductility were 
improved66 (Fig. 3e). Control of solidification morphol-
ogy by adjusting parameters that affect the temperature 
gradient and solidification rate as well as addition of a 
suitable inoculant has worked for several alloys and AM 
variants, but more work is needed to establish a database 
for controlling microstructures.
There are other approaches for promoting CET. For 
example, high-​intensity ultrasound was used to achieve 
CET for both Ti–6Al–4V and Inconel 625 without requir-
ing any changes in the process parameters or the addi-
tion of grain refiners74. Ultrasonic irradiation agitated 
the melt to produce a large number of nuclei in the alloy 
during solidification74. However, the application of this 
method requires modification of the printing equipment 
to enable generation of high-​intensity ultrasound.
Texture
Texture, the non-​random distribution of crystallogra­
phic orientations of a polycrystalline material, affects the 
properties of printed parts. These properties include 
the elastic modulus75, yield and tensile strengths76, duc-
tility76, fatigue resistance77, corrosion behaviour78,79, 
creep80 and coefficient of thermal expansion. In metal 
printing, the regrowth of grains from previous layers 
is the source of columnar grains that grow epitaxially 
from the existing grains and tend to align with them63. 
This behaviour is modified by the size and shape of 
the molten pool, which tends to preferentially align the 
growing grains along the direction of local heat flow81. 
In PBF, columnar grains typically form along the growth 
direction66, whereas in DED the direction of grain 
growth may deviate from the build direction82. The strik-
ing differences in the shape and size of the fusion zone in 
the two processes are contributing factors. However, 
in PBF and DED processes, texture is influenced by the 
competitive growth of grains depending on the direction 
of maximum heat flow as well as the preferred direction of 
crystal growth26,63,72.
Texture creates anisotropic mechanical properties 
in the part, and it can be modified by post-​build heat 
treatment83. During the building of parts, texture has 
been adjusted by varying the scanning speed, layer 
thickness, heat input, beam size and hatch spacing84–86. 
For example, texture of a cobalt-​based alloy during laser 
deposition87 was found to be affected by the scanning 
speed. The scanning strategy81,88,89, processing variables 
and material systems84 also affect texture. Experimental 
measurements of texture by electron backscatter dif-
fraction90, X-​ray diffraction, ultrasonic evaluation91,92 
or neutron diffraction tend to be time consuming and 
expensive93, so computational methods after rigorous 
validation are emerging to predict texture from the 
AM build parameters94. For example, the computed 
solidification patterns and the optical micrographs of 
the deposited Inconel 718 specimen for unidirectional 
and bidirectional scanning show the directions of grain 
growth (Fig. 3f). Striking differences82 in the computed 
and the observed solidification textures owing to 
changes in laser scanning pattern during AM are also 
observed (Fig. 3f). The results show that modelling can 
predict and customize solidification textures.
Common defects
Defects such as voids and lack of fusion95, cracking66, 
residual stresses96, distortion96 and surface roughness all 
affect the properties and serviceability of parts. Voids 
can form owing to lack of fusion95, keyhole instability97,98 
or gas-​generated porosity99. If the laser or electron beam 
heat source is too intense, keyhole formation can occur 
with associated pores if the keyhole collapses due to 
instability97. If the heat source is not intense enough, the 
molten pool can be too shallow relative to the AM layer 
thickness or too narrow relative to the track spacing, 
resulting in a lack of fusion defects where insufficient 
molten metal is present to fuse the feedstock into the 
existing layer95. Porosity can occur whenever the feed-
stock or process conditions are such that oxygen, nitro-
gen, hydrogen or other gaseous elements are dissolved 
into the molten pool and, later, nucleate pores as the 
pool solidifies and gas solubility decreases100. The con-
taminant elements can come from external sources, such 
as improper inert gas shielding100, or from gases within 
the powder or wire feedstock101. Post processing using 
hot isostatic pressing may be performed to minimize 
porosity and improve fatigue strength1,102–104.
Cracks may form in AM parts during solidification 
and cooling to room temperature and are similar to the 
cracks that form during welding in crack-​susceptible 
microstructures66. Solidification cracking is affected by 
the volumetric shrinkage of the molten pool depen­
ding on the alloy properties and liquid feeding in the 
inter-​dendritic region during solidification. Solid­
ification and liquation cracking occur in the fusion 
zone and the partially melted zone, respectively, when 
low melting-​point phases create liquid films at grain 
boundaries that are pulled apart by tensile stresses dur-
ing solidification66. The cracking sensitivity could be 
evaluated through a criterion105 considering the sepa-
ration of grains from each other, the lateral growth of 
grains and the ease of liquid feeding between grains.
Residual stresses develop from a liquid-​to-​solid 
change of state, thermal contraction and expansion, and 
from the use of fixtures, support structures and other 
forms of restraints96,106. In addition, solid-​state phase 
transformations such as from austenite to ferrite in 
steels can contribute to residual stresses106. The stresses 
themselves can be large enough to cause delamination 
www.nature.com/natrevmats
Reviews
54 | January 2021 | volume 6	


between AM layers in low-​ductility alloys such as 
Ti–6Al–4V (ref.107), particularly if the part has other 
defects such as porosity or lack of fusion defects that may 
act as sites for stress concentration108. Residual stresses 
increase with the amount of restraint on the part being 
built109 and tend to be lower for high heat inputs. As a 
consequence, heat treatment over long times allows the 
stresses to diminish. Distortion of AM parts depends 
on residual stresses, restraints, part stiffness and heat 
input96. Distortion can occur as the layer-​by-​layer part 
is created, causing the part to deviate from its intended 
geometry in a way that can be detrimental if precise 
dimensions are required110.
Surface roughness and waviness are common in 
AM parts. Post-​build processing, such as machining, 
grinding, chemical treatment or polishing, is often used 
to achieve a smooth surface111,112. The source of surface 
roughness depends on the sizes of the powder particles 
and processing conditions, and the surface waviness 
scales with the layer thickness113,114. Processes with high 
deposition rates, such as DED115, make parts with more 
waviness than processes with low deposition rates, such 
as PBF113. However, the surfaces of the parts fabricated 
by PBF tend to be no smoother than the size of the 
largest powder particles, because unfused particles are 
observed near the solidified molten pools116.
The scan strategy involves the remelting and sequen-
tial changes of the scan path direction coupled with the 
selection of the laser power and scan speed to optimize 
the reduction of porosity, lack of fusion, density, distor-
tion and processing time. These difficulties have been 
shown to vary with the laser power, scan speed and hatch 
spacing. Porosity is frequently observed at the start or 
stop regions of a scan path or between the fusion zones 
of adjacent scan paths100.
To conclude, it is difficult to control attributes of the 
printed parts by the selection of process parameters 
and feedstocks. These difficulties originate largely from 
the scarcity of quantitative frameworks that can cor-
relate processing conditions with product attributes. 
Mechanistic models and machine learning address this 
difficulty by reducing the ranges of AM process variables 
to create parts with the desired attributes before parts are 
built while at the same time minimizing development 
times and costs.
Mechanistic models
Mechanistic models enable calculations of variables 
such as temperature and velocity fields, cooling rates 
and solidification parameters that are not easily meas-
ured during AM. These models provide a phenome-
nological description of how the microstructure and 
properties of an AM part evolve from process variables 
and the thermophysical properties of the feedstock. 
However, mathematical representation of the process 
and the product attributes is a challenging undertaking. 
This complexity is addressed, almost always, by model-
ling the most important physical processes and ignor-
ing the less important processes. These assumptions 
compromise fidelity, the extent of which is checked 
by comparing model predictions with experimental 
results. In addition, the task is often leveraged using the 
experience of building models of fusion welding and 
metallurgy.
Mechanistic models of AM are widely used to pre-
dict the relationships between process variables and the 
attributes of parts. Table 2 summarizes some common 
mechanistic models, and their features and applications 
in metal printing. Many of the physical processes need 
to be represented in multiple length scales, and in some 
cases over varying timescales. Most of the simulations 
require transient 3D temperature fields. Considerable 
variation in the computational efficiency is achieved 
depending on the physical processes considered and 
the scale of calculations. When the calculations are per-
formed on the mesoscale, they are fairly rapid. However, 
the same calculations in powder-​scale models take 
orders of magnitude more time117. Therefore, linking 
of timescales and length scales is challenging and needs 
further research. Here, we examine the progress made 
and the opportunities and challenges in the mechanistic 
modelling of metal printing.
Models of heat transfer and metal flow
Metal printing involves heating, melting, solidifica-
tion and solid-​state phase transformations as well as 
the evolution of fusion zone geometry, microstructure, 
grain structure, defects, mechanical properties, residual 
stresses and distortion. A quantitative understanding of 
these physical processes and the attributes of the parts 
starts with simulation of the transient temperature field 
and the flow of liquid metal in the fusion zone. The heat 
transfer and fluid flow calculations are typically based 
on the equations of conservation of mass, momentum 
and energy to obtain important variables such as the 
temperature–time history, fusion zone geometry and 
solidification growth rates118–120. Figure 4a shows typical 
examples of the temperature and velocity fields of the 
molten pool during PBF-​L, DED-​L using powder and 
DED-​GMA using wire feedstocks120–122. The 3D tem­
perature distributions and geometries of the molten 
pool and the feedstock materials can be captured by 
the transport phenomena-​based mesoscale models. 
These models can simulate deposition of parts in mul-
tiple layers, with each layer containing multiple tracks 
or hatches.
AM relies on the localized melting and solidification 
of feedstock materials and, as a result, the shape and 
size of the molten pool influence the microstructure 
and properties of the printed parts. Apart from calcu-
lating the geometrical features of the part, these models 
can calculate multiple thermal cycles experienced by the 
deposited metal during the build process. These results 
provide temperature–time data at various monitoring 
locations118 (Fig. 4b). The thermal cycles are necessary for 
predicting microstructures. The experimental measur­
ement of such exhaustive temperature–time–space 
data is challenging owing to the complex nature of 
AM. However, temperature–time data in several loca-
tions, when available, are useful to test and calibrate the 
models. The results obtained from the heat transfer and 
fluid flow models enable a quantitative understanding 
of the evolution of microstructure, grain structure and 
assessment of printability123,124.
nature Reviews | MAteRiAlS
Reviews
	
 volume 6 | January 2021 | 55


Simulation of microstructure evolution
Modelling of phase fractions of various constituents in 
the microstructure helps to understand the properties of 
printed parts both before and after their post-​build heat 
treatment. Each heat-​treatable alloy undergoes unique 
phase transformations during heating and cooling. As a 
result, modelling of microstructures is alloy-​specific 
and represents the various pathways for each phase 
transformation involved in the evolution of micro-
structure125. There is a rich literature of microstructure 
calculations in multipass fusion welding where metallic 
materials are subjected to multiple thermal cycles, just 
like in AM processes1. In these systems and AM, reliable 
microstructure calculations have been achieved using 
detailed kinetic information126 manifested in continuous 
cooling transformation diagrams and relations of phase 
fractions with time, such as the Johnson–Mehl–Avrami 
equation.
Simulations of phase transformations and the scale 
of microstructural features have been attempted con-
sidering the thermal history and alloy composition127,128. 
Microstructure calculations using the Johnson–Mehl–
Avrami equation have been useful for PBF-​L of the 
Ti–6Al–4V alloy129, and continuous cooling transforma-
tion diagrams have been used130 to understand micro-
structure evolution during DED-​L of Ti–6Al–4V and 
for simulating precipitation kinetics during DED-​L of 
Inconel 718 (ref.131). Although these calculations pro-
vide reliable results of phase fractions, they do not provide 
morphological information. Phase field simulations 
are used to resolve microstructural features in small 
length scales132. For example, phase field simulations 
Table 2 | Common mechanistic models for the simulation of metal printing
Purpose
Model
Features
Applications
Calculation of 
heat, mass and 
momentum 
transfer
Part scale heat 
conduction model
Fourier heat conduction equation is solved either analytically  
in 1D or 2D or numerically in 3D
Does not consider the effects of molten metal flow inside the 
pool and often provides inaccurate results
Temperature fields188; fusion zone 
geometry189; cooling rates190
Part scale heat transfer 
and fluid flow
Solves 3D transient conservation equations of mass, momentum 
and energy
Considers the effects of molten metal flow inside the pool  
and therefore provides accurate temperature distribution and 
deposit geometry
Temperature and velocity 
fields119; fusion zone geometry121; 
cooling rates120; solidification 
parameters122; lack of fusion121
Part scale volume  
of fluid and level  
set methods
Tracks the free surface of the molten pool
Computationally intensive
Accumulates errors and the calculated deposit shape and size 
often do not agree well with experiments
3D deposit geometry191; 
temperature and velocity 
fields191; cooling rates192; 
solidification parameters192
Powder-​scale models
Involves free surface boundary conditions treating 
thermodynamics, surface tension, phase transitions and wetting
Small timescale and length scale, computationally intensive
Lattice Boltzmann or arbitrary Lagrangian Eulerian
Temperature and velocity 
fields117; track geometry193;  
lack of fusion143; spatter143; 
surface roughness194
Microstructure, 
nucleation and 
grain growth 
prediction
TTT-​baseda, CCT-​basedb 
and JMA-​basedc models
Based on phase transformation kinetics during cooling
Widely used for simulating phase transformations in steels and 
common alloys
High computational efficiency
Solid-​state phase transformation 
kinetics195
Monte Carlo method
A probabilistic approach of grain orientation change
Provides grain size distribution with time
High computational efficiency
Grain growth63; solidification 
structure26; texture40
Cellular automata
Simulates growth of grain and subgrain structure during 
solidification
Medium accuracy and computational efficiency
Solidification structure196;  
grain growth197; texture197
Phase field model
Simulates microstructural features and properties by calculating 
an order parameter based on free energy that represents the 
state of the entire microstructure
Computationally intensive
Nucleation132; grain growth198; 
evolution of phases198; precipitate 
formation199; solid-​state phase 
transformation199
Calculation of 
residual stresses 
and distortion
FEA-​basedd 
thermomechanical 
models
Solves 3D constitutive equations considering elastic, plastic and 
thermal behaviour
Many software packages exist, and these are easy to implement 
and can handle intricate geometries
Adaptive grid and inherent strain method are often used to 
increase calculation speed
Evolution of residual stress200; 
strains138; distortion201; 
delamination165; warping165
CCT, continuous cooling transformation; FEA, finite element analysis; JMA, Johnson–Mehl–Avrami; TTT, time–temperature–transformation. aTTT diagrams provide 
the effects of time and temperature on microstructure development of an alloy at constant temperature. bCCT diagrams indicate the phase changes during 
cooling. cThe JMA equation provides the extent of phase transformations with time. dFEA is a numerical method to solve complex non-​linear equations.
www.nature.com/natrevmats
Reviews
56 | January 2021 | volume 6	


Top surface
0
3
6
Width (mm)
Width (mm)
0
3
6
9
12
15
18
21
24
27
30
Length (mm)
Length (mm)
0
3
6
d  Residual stresses and distortion
4 mm
1,000 800
400
80
–30 –200 –600
PBF-L
DED-L
DED-GMA
b   Microstructure
Temperature (K)
0
600
1,200
1,800
Time (ms) 
300
9,00
1,500
2,100
Layer 1
Layer 2
Layer 3
a   Temperature and velocity ﬁelds
77
0
10
12
15
18
21
5
DED-L
e  Defect formation
Void formation
Molten pool 
100 μm
Keyhole pore
Temperature
300 K
1,700 K
1,400 K
1,000 K
700 K
High stress owing
to large pool
Low stress owing
to thin layers
z
x
y
Longitudinal residual stress (MPa)
c  Solidiﬁcation and grain growth
2 mm from top surface
0
3
6
9
12
15
18
21
24
27
30
100 μm
Primary dendrites
Secondary dendrites
50 μm
100 μm
5 μs
100 μm
100 μm
N0
 = 5×1013 m–3
N0
 = 5×1014 m–3
N0
 = 5×1015 m–3
10 μm
20 μs
PBF-L
Temperature (K)
Temperature (K)
Temperature (K)
1,693 1,733 1,900 2,300
1,693 1,733 1,800 1,900 2,000 2,500
600
900
1,585 1,725 1,900
Depth (mm)
Width (mm)
Length (mm)
Length (cm)
DED-GMA
500 mm s–1
20 cm s–1
Depth (mm)
Length (mm)
3,000 mm s–1
0.97
1.00
1.03
20.05
20.15
20.25
20.35
Width (mm)
1.03
1.08
1.13
1.18
1.5
1.4
1.3
1.2
1.1
1.0
0.9
79
83 85 87 89 91
81
Fusion
line
nature Reviews | MAteRiAlS
Reviews
	
 volume 6 | January 2021 | 57


of microstructure evolution133 in an aluminium alloy 
show dendritic growth (Fig. 4b). Phase field simulations 
have also been applied for microstructure calculations 
in nickel-​based superalloys134. Solid-​state phase trans-
formation from a beta phase to a basket-​weave alpha 
phase that occurs during DED-​L of Ti–6Al–4V (ref.135) 
has been investigated using a phase field model with 
temperatures computed from a powder-​scale model. 
In these models, it is challenging to represent physi-
cal processes such as nucleation, heating and cooling 
considering fluid flow in 3D, and the specification of 
energy density fields especially at boundaries. Lack 
of quantitative comparisons of the evolution of phase 
fractions with experimental data and the computation-
ally intensive nature of the 3D calculations at length scales 
comparable with the dimensions of the part add to the 
difficulties.
Calculation of grain structure evolution
The morphology, dimension and orientation of the 
grains affect the mechanical and chemical properties 
of parts. The spatial variations of grain size and mor-
phology can be observed through serial sections along 
different directions. However, the procedure is time 
consuming. Also, depending on the plane selected, 
columnar grains may appear to be equiaxed grains in 
some sections. Models of grain growth based on Monte 
Carlo simulations or cellular automata have been used 
to understand the grain structure of printed parts. 
These models26,63,136,137 can simulate the transition of 
different grain morphologies such as columnar to equi-
axed grains, the variation of grain growth directions 
under location-​dependent solidification conditions26 
and the solid-​state grain growth under multiple ther-
mal cycles63. The computed influence of nuclei density 
on the grain morphology shows that the quantities of 
equiaxed grains increase with the nuclei density and 
CET was observed where the nuclei density was large127 
(Fig. 4c, left).
The 3D grain growth model can uncover the evolu-
tion of grain structure and provide information about 
the morphology, dimension and orientation of the grains 
and texture26,63,127. These calculations require 3D tran-
sient temperature fields, fusion zone geometries, local 
temperature gradients and solidification growth rates at 
various locations, all of which can be obtained from heat 
and fluid flow modelling. Grains grow epitaxially from 
the partially melted grains and follow the maximum heat 
flow directions at the solidification front26,63. Modelling 
of grain structure in 3D is important because columnar 
grains may appear equiaxed in certain cross-​sections26,63 
(Fig. 4c, right).
Modelling residual stress and distortion
Experimental determination of the evolution of stresses 
and distortion is challenging1 but thermomechanical 
models96,138 are widely used. These models are compu-
tationally intensive and are mostly based on heat con-
duction models that ignore liquid metal flow, which is 
typically the main mechanism for heat transfer within the 
molten pool. More accurate calculations that consider 
convective heat transfer are emerging with improve-
ments in computational software and hardware. The dis-
tributions of residual stresses and strain along the laser 
scanning route vary significantly during PBF-​L, DED-​L 
and DED-​GMA123 (Fig. 4d). These calculations consider 
convective heat transfer and reveal that PBF-​L shows 
minimum residual stresses and distortion because of the 
small size of the molten pool and the low deposition rate. 
Where computationally intensive calculations are not 
practical, back of the envelope analytical calculations139 
provide a means to mitigate distortion.
Models of defect formation
In mesoscale modelling, small-​scale features such as 
surface roughness are not simulated. Powder-​scale mod-
els are suitable for resolving these issues, because these 
models typically simulate 1 mm3 or smaller volumes 
with a mesh size down to 1–2 μm140. The time step is 
often restricted to a few nanoseconds to maintain com-
putation convergence at small grid spacing and high 
velocities of liquid metal flow140. Thus, these models 
can take a day or more, in multiprocessor computers, 
to simulate very small domains141. Void formation due to 
keyhole instability can be simulated by a powder-​scale 
model (Fig. 4e).
Mechanistic models for the formation of various 
defects, such as porosity, loss of alloying elements and 
cracking, are emerging. Pores may form owing to lack 
of fusion during PBF and DED in commonly used AM 
alloys121. Keyhole induced pores were also simulated at 
high energy intensities capturing the unstable nature 
Fig. 4 | Results from various types of mechanistic models for metal printing.  
a | Temperature and velocity fields in the molten pool of SS 316 stainless steel using 
continuum mechanics120–122 for powder bed fusion with a laser (PBF-​L), directed energy 
deposition with a laser (DED-​L) and directed energy deposition with a gas metal arc 
(DED-​GMA). The shape and size of the molten pool vary significantly for the different 
processes because of differences in process variables such as the power of the heat 
source and scanning speed. b | Plot of temperature as a function of time at a monitoring 
location showing multiple thermal cycles in different layers during DED-​L of SS 316 
(ref.118) (left). Phase field simulation of dendritic growth for gas tungsten arc welding of 
2A14 aluminium alloy (ref.133) shows qualitative agreement between the experimentally 
observed microstructure on the left and the theoretically calculated microstructure on 
the right (middle). Phase field simulations of microstructure evolution electron beam 
additive manufacturing of Ti–6Al–4V (ref.241) showing temporal growth of beta phase 
columnar grains (right). c | The influence of nuclei density, N0, on the morphologies of 
grains during PBF-​L of SS 304 stainless steel shows that columnar to equiaxed transition 
is favoured at high nuclei density (left)127. Monte Carlo simulation of grain growth during 
gas tungsten arc welding of 1050A aluminium alloy shows that columnar grains may 
appear equiaxed at certain cross-​sections because of the curvature of the columnar 
grains (right)26. d | Thermomechanical modelling of longitudinal residual stress and 
distortion in SS 316 parts made by PBF-​L, DED-​L and DED-​GMA showing lower residual 
stress for PBF-​L123. e | Powder-​scale modelling of defect formation such as voids in PBF-​L 
of Ti–6Al–4V. The shape and size of voids and their spatial distributions depend on the 
temperature field, molten pool geometry and powder size (left). Inappropriate selection 
of the power density of the laser beam causes porosity during keyhole-​mode PBF-​L of  
SS 316, which is simulated using a powder-​scale model (right)242. Panel a (middle) adapted 
with permission from ref.122, Elsevier. Panel a (right) adapted with permission from ref.120, 
Elsevier. Panel b (left) adapted with permission from ref.118, AIP. Panel b (middle) adapted 
with permission from ref.133, Elsevier. Panel b (right) adapted from ref.241, Springer Nature 
Limited. Panel c (left) adapted with permission from ref.127, Elsevier. Panel c (right) 
adapted with permission from ref.26, Elsevier. Panel d adapted from ref.123 copyright © 
Institute of Materials, Minerals and Mining, adapted by permission of Informa UK 
Limited, trading as Taylor & Francis Group. Panel e (right) adapted from ref.242,  
Springer Nature Limited.
◀
www.nature.com/natrevmats
Reviews
58 | January 2021 | volume 6	


of keyhole walls142,143. Another important issue is the loss of 
alloying elements during the high temperature dep-
osition. The selective loss of volatile alloying ele-
ments may result in a significant difference between 
the chemical composition of the feedstock and the 
deposit123,124. The change in composition also affects 
the microstructure and properties of the deposit.
The successful printing of many alloys is hindered 
by the cracking susceptibility1 associated with the 
melting and solidification processes. Massive cracking 
often occurs at the boundaries of the columnar grains. 
Alternating the grain morphology from columnar 
to equiaxed can suppress the formation of solidifica-
tion cracking and thus improve the printability of the 
alloy. Several approaches related to the metallurgy of 
CET are discussed above in ‘Columnar to equiaxed 
transition’. All of these approaches need quantitative 
evaluations of the solidification conditions with 
appropriate transport phenomena and grain structure 
evolution models.
Estimation of printability
Printability is evaluated by examining susceptibilities of 
parts to common defects such as distortion, composition 
change, lack of fusion and cracking123,124. Comprehensive 
and reduced order models are available to undertake 
this task. A theoretical scaling analysis has been used 
to test the vulnerability of alloys to thermal distortion. 
Susceptibilities of alloys to lack of fusion defects has 
been calculated using numerical heat transfer and fluid 
flow calculations. A model-​based printability database 
after experimental validation can reduce trial and error 
testing and expedite qualification of parts, and thus save 
time and money for the printing of new alloys.
At present, only a handful of commercial alloys 
can be easily printed, and the design of alloys specifi-
cally for AM is just beginning. An important goal is to 
improve the printability of alloys by making alloys less 
susceptible to common defects. For example, DED-​L 
parts made from powders of Cr–Mo–V tool steel and 
a maraging steel exhibited superior mechanical proper-
ties to those from the individual steels144. Powder blends 
of titanium and chromium have been printed using 
DED-​L to achieve good strength and ductility145. Silicon 
has been added to 2024, 6061 and 7075 aluminium 
alloys to reduce cracking arising from higher fluidity, 
decreased melting range, thermal expansion and solid-
ification shrinkage146. Addition of rare earth elements 
such as scandium or zirconium to aluminium alloys 
resulted in fine precipitates of Al3Zr or Al3Sc that acted 
as inoculants for the grain refinement and prevention of 
cracking146. A new nickel-​based Hastelloy was designed 
to prevent cracking during PBF-​L73.
Mechanistic models are powerful simulation tools 
that provide otherwise unobtainable insight12. However, 
these calculations require an understanding of underly-
ing physical mechanisms that are not always available. 
In addition, mechanistic models are often complex and 
require significant computational resources and user 
skills. In contrast, machine learning requires less pro-
gramming and modelling skills and, as a result, is being 
widely applied.
Machine learning in metal printing
Machine learning enables computers to make reliable 
predictions147,148 by learning from data gathered from 
various sources. Useful information and relationships 
are extracted from data without phenomenological 
guidance or explicit programming. The accuracy of 
the predictions improves with the quality and volume 
of data. The availability of powerful open source pro-
grams facilitates their use for solving complex problems 
in metal printing that may appear intractable at first. 
Here, we examine the need for machine learning in 
metal printing, outline the availability of open source 
algorithms and codes, and discuss their effective use and 
impact in metal printing.
Reasons to use machine learning
Building high-​quality parts by trial and error adjust-
ment of multiple process variables is neither rapid nor 
cost-​effective. As a result, machine learning149–155 has 
been widely used in all steps of metal printing (Fig. 2). 
Evolution of the microstructure, properties and defects 
in metal printing depends on multiple simultaneously 
occurring physical processes. Therefore, unified, pheno­
menological predictions of the product attributes are 
not available. Machine learning can serve as a tool to 
predict the microstructure, properties and defects. 
It does not require the solution of complex equations based 
on phenomenological understanding and, as a result, 
the calculations are rapid149. In addition, the hierarchy 
of the input variables and their sensitivity on the out-
put can be determined155. Finally, machine learning 
programs are easy to build owing to the availability of 
well-​tested, easy to use and reliable algorithms.
Wide availability of resources
The application of machine learning in AM has been 
facilitated by machine learning models and open source 
programs (Table 3). Models for classification such as 
the decision tree, random forest and k-​nearest neigh-
bour are useful for data-​classifying problems, such as 
the ‘detected’ or ‘not-​detected’ pores in printed parts. 
These models are also used for decision-​making. 
Regression-​based models such as artificial neural net-
works, Bayesian networks and support vector machines 
are used to correlate the inputs and outputs based on a 
function and can predict the values of the output varia-
bles for a set of input parameters. Open source programs 
such as Weka, Scikit learning, TensorFlow, Keras and 
Theano can be easily used because they are accompa-
nied by extensive manuals and test cases. In the next sec-
tion, we examine the applications of machine learning 
in various phases of building metallic parts to improve 
product quality.
Applications in metal printing
The adoption of machine learning in metal printing 
has been driven by the need to manage process com-
plexity and the availability of powerful open source 
codes. Recent applications range from process planning 
to parameter optimization, sensing and control, and 
result in improved fusion zone attributes, tailored micro-
structures and defect mitigation (Fig. 5). These examples 
nature Reviews | MAteRiAlS
Reviews
	
 volume 6 | January 2021 | 59


illustrate the important role of machine learning in 
metal printing, either alone or in combination with 
mechanistic models.
Process parameter optimization. The selection of process 
parameters is the most important factor in controlling 
the quality of the part. Machine learning is a fast and 
reliable way to predict and optimize process conditions 
to achieve the desired attributes of a part (Fig. 5a). For 
example, neural networks for DED-​GMA predicted the 
wire-​feed rate, scanning speed, arc voltage and nozzle-​
to-​plate distance to achieve the required width and 
height of the part156,157. A random forest algorithm was 
used to optimize process parameters to print good qual-
ity Inconel 718 parts using PBF-​L158. Neural networks 
were used to predict translational and rotational speeds 
of the powder-​spreading roller to minimize surface 
roughness159. A thermodynamic model was augmented 
with machine learning to identify process conditions 
to avoid the formation of a brittle intermetallic sigma 
phase during DED-​L of a graded component between SS 
316L and pure chromium36. Regression-​based machine 
learning160 was used to examine the influence of the feed 
rate, hatch spacing, laser power and powder feed rate of 
DED-​L on the surface properties. The aforementioned 
applications of machine learning to build parts of several 
alloys using multiple AM variants indicate its ability to 
optimize process parameters based on data. The optimi-
zation of process parameters is improved as more data 
are accumulated with time.
Sensing and process control. Machine learning can be 
used to monitor and control metal printing, and, hence, 
to mitigate defect formation and improve dimen-
sional accuracy. For example, in situ photographs of 
a part taken by a camera can be compared with the 
Table 3 | Machine learning models, open source computer programs and their applications in metal printing
Machine learning
Description and features
Applications in metal printing
Machine 
learning 
models
Artificial neural 
networks
Layers of hidden nodes connect input and output 
variables; an activation function is used to connect 
nodes with each other; errors in predictions are 
minimized by adjusting weights for each connection
Defect recognition202; geometry prediction167; 
thermal deformation compensation203; process 
parameter optimization204; anomaly detection174; 
quality monitoring205,206; topology optimization207
Decision tree
Progressively classifies a group of variables based on 
rules and displays them as an upside-​down tree; the root 
of the tree often displays the most important variable 
and the apex shows the least important variable
Surface roughness reduction208; porosity 
prediction173; dimensional variation209; printing speed 
modelling210; design considering residual stresses and 
support requirement211
Support vector 
machines
Used for classification and regression, the model can 
split data into groups based on their locations in feature 
space; the features of the data fully determine their 
locations and there is no stochastic element involved
Defect detection212; real-​time composition 
monitoring213; surface roughness153; tensile strength 
prediction214; construction of process maps151; 
monitoring temperature field215
Bayesian 
networks 
or Bayesian 
classifiers
A statistical model that represents the probabilistic 
relation between cause and effect; the conditional 
probabilities are computed using Bayes’ theorem
Quality inspection216; fault diagnosis217; thermal field 
prediction218; porosity prediction219; optimization 
of process parameters220; prediction of fusion zone 
depth221
k-​nearest 
neighbour
Separates data into different classes based on the 
attributes or the class of the majority of the nearest 
neighbours; the number of nearest neighbours, k, is 
selected by trial and error
Quality monitoring154; printing speed monitoring210; 
porosity prediction173; dimensional variation209; 
design of metamaterials222
Random forest
Consists of multiple decision trees, each with a 
classification; the forest gets a classification from the 
attributes of the greatest number of trees; for regression, 
the model considers the average of the outputs of 
different trees
Surface roughness determination208; tensile strength 
prediction214; reducing macro porosity and cracks223; 
printing speed monitoring210; minimize porosity  
by optimizing parameters158
Open source 
computer 
programs
Weka
Written in Java; used for classification, clustering, 
regression and visualization; available from https:// 
www.cs.waikato.ac.nz/ml/weka/citing.html  
(online course available)
Image classification-​based defect detection224; 
energy consumption in additive manufacturing225; 
data classification226; fault diagnosis217; porosity 
reduction227
Scikit learning
Written in Python, Cython, C and C++; used for 
classification, clustering and regression; available  
from https://scikit-​learn.org/stable/
Printing speed modelling210; dimensional accuracy228; 
temperature profile prediction229; relation between 
several microstructures230; process monitoring163; 
grain structure simulation231
TensorFlow
Written in Python, C++ and CUDA; used for neural 
network and data flow programming; available from 
https://www.tensorflow.org/
Dimensional accuracy228; defect detection232; 
mechanical behaviour of structures233; online 
monitoring of part quality150; molten pool images234
Keras
Cross-​platform neural network library written  
in Python; runs on multiple platforms; available from  
https://keras.io/
Distortion prediction235; thermal history prediction236; 
dimensional accuracy228; quality monitoring237
Theano
Written in Python; Windows, Linux and Mac operating 
systems; available from http://www.deeplearning.net/
software/theano
Defect detection238; prediction of part weight and 
building time239
www.nature.com/natrevmats
Reviews
60 | January 2021 | volume 6	


Machine learning variable 1
a  Parameter optimization using machine learning
3D printing machine
Printed part
CPU
Variable 1
Variable 2
Variable 3
Variable 4
Machine learning
 variable 2
Desired process
conditions
b  Process monitoring and control
Measured temperature
Classiﬁcation of abnormal
conditions for defect formation
e  Defect mitigation
Machine learning variable 2
Machine learning variable 1
–200
–200
–100
–300
–100
0
100
200
0
100
Normal
Abnormal
Width (mm)
Length (mm)
1,636
A part printed using abnormal
condition shows defects
Classiﬁer 
Simulated grain growth
d  Microstructure control
Grain size (μm)
0
10
20
30
40
0.025
0.020
0.015
0.010
0.005
0
Frequency
Size distribution by machine learning
–0.4
–0.2
–0.3
0.3
–0.1
0.1
0
0.2
Model prediction
Machine learning prediction
Training data
Testing data
Camera image
CAD
Powder bed
Part
Laser beam
CPU
Camera
Distance
Distance
Distance
Distance
With ﬂaw
Without ﬂaw
100
80
60
40
20
Values of a variable indicating a ﬂaw are used in the
neural network to control the process
Sensing image and CAD design
are compared to detect ﬂaws
c  Fusion zone attributes
z
x
y
Longitudinal
Transverse
Track width using
neural network (mm)
0.4
0.3
0.2
0.1
0.0
Training
Testing
x
x
Measured track width (mm)
0.0
0.1
0.2
0.3
0.4
Laser power (W)
Measured track width (mm)
0.4
0.3
0.2
0.1
0.0
100
200
300
400
Different scanning speeds (mm s–1)
100
130
160
190
220
250
280
310
340
370
400
nature Reviews | MAteRiAlS
Reviews
	
 volume 6 | January 2021 | 61


computer-​aided design to detect regions of interest 
that may contain flaws in a layer. These regions can be 
subdivided into several subregions with complex spa-
tial patterns in the images that can be used to train a 
neural network to detect flaws in real time with good 
accuracy161 (Fig. 5b). Three examples demonstrate vari-
ous sensing and control methods. First, data on powder 
characteristics obtained using computer vision algo-
rithms are used to train a support vector machine for 
process control162. Second, a process monitoring system 
augmented with a multilayer classifier163 can provide 
control strategies for minimizing defect formation in 
PBF-​L, based on data provided by identical machines 
producing the same part. Last, data from an optical sen-
sor were analysed164 using a support vector machine to 
detect defects during DED-​L. These examples show the 
viability of in situ monitoring and control of the printing 
process with minimum human intervention.
Control of part geometry. Part geometry can devi-
ate from the design specifications owing to instability 
in the printing process, and thermal distortion, and 
the deviation may result in part rejection in extreme 
cases2,9,96,138,165. Machine learning is often used to control 
part geometry during the printing process. For exam-
ple, deposit widths measured using a high-​speed camera 
during PBF-​L of SS 316 for different laser powers and 
scanning speeds were used to train a neural network166 
(Fig. 5c, left). In another case, the neural network pre-
dicted the track width for a given scanning speed and 
laser power, which agreed well with the experimental 
results (Fig. 5c, right).
Neural network-​based machine learning was used 
to control the deposit width and height, and the fusion 
zone depth, during DED-​L of an aluminium alloy167. 
In addition, molten pool depth in PBF-​L was controlled 
by optimizing laser power, scanning speed, spot size 
and absorptivity using a decision tree168. Furthermore, 
shape deviations were captured during the process 
and analysed using a neural network to achieve better 
geometric tolerance of AM parts169. These examples 
demonstrate the improved compliance with the geomet-
ric specifications of the design ultimately facilitating part 
qualification.
Tailoring microstructure and properties. Microstructural 
features such as grain size, distribution and orientation 
as well as properties such as tensile strength, hardness 
and fatigue life were used to develop machine learning 
algorithms that could rapidly compute processing con-
ditions to achieve the desired microstructure and pro­
perties170. Input data for the training of machine learning 
can be generated from calibrated mechanistic models. 
For example, the results of frequency as a function of 
grain size computed using a 3D Monte Carlo model can 
be used to train a neural network (Fig. 5d). This neural 
network could rapidly predict grain growth, which 
matched well with the predictions from the computa-
tionally intensive Monte Carlo method171 (Fig. 5d). A pro-
cess model for PBF-​EB supported by a neural network 
and a genetic algorithm predicted yield strength to aid 
in understanding the processing structure–property 
relationship for PBF process172. Although progress has 
been made in quantifying microstructural features using 
machine learning, the applications of machine learning 
to control microstructure and properties during metal 
printing remain in their initial stages of development.
Reducing defects. Machine learning has been used 
to minimize defects such as porosity, lack of fusion, 
distortion and surface roughness in parts. For exam-
ple, machine learning has minimized the porosity in 
Ti–6Al–4V parts printed using DED-​L173 (Fig. 5e). More 
specifically, an infrared camera monitors the temper-
ature field during the DED-​L process, from which a 
molten pool boundary is extracted by tracking the 
solidus temperature contour. From the data, a support 
vector machine is developed that classifies the process 
conditions into two categories, normal and abnor-
mal, based on the probability of porosity formation. 
When experiments were performed using the condi-
tions for porosity formation, defects were found in the 
part (Fig. 5e). In another example, the anomalies in pow-
der spreading by a recoater (a blade that spreads powder 
during PBF-​L) were detected by a computer vision sys-
tem174. Imperfections of the powder bed resulting from 
recoater streaking and hopping were correlated with part 
defects using a neural network. In other studies, auto-
mated image analysis has been used to detect anomalies 
during the powder spreading of PBF-​L to identify defects 
using machine learning175. Machine learning provides an 
excellent framework for the reduction of surface defects, 
the origin of which are not always known.
Other applications. Apart from the various stages of 
building parts, machine learning has other uses in metal 
printing, including powder characterization, part fail-
ure and in situ part inspection. For example, a support 
vector machine trained using the data from computer 
Fig. 5 | Applications of machine learning in metal printing. a | Schematic diagram 
showing the optimization of process parameters to obtain a desired attribute of a part, 
such as the deposit width, which depends on many process variables (variables 1–4).  
In machine learning, process variables are sometimes combined into fewer machine 
learning variables (machine learning variables 1 and 2) that can be obtained from the 
available data. These variables can be used to train a machine learning program to 
classify data (for example, greater than a specified width) or quantitatively correlate 
variables in the data with a target attribute (for example, deposit width). b | Optical 
images from each layer of a Ti–6Al–4V part is compared with the computer-​aided design 
(CAD) file to identify regions of interest in the image that may include flaws during 
powder bed fusion using a laser heat source (PBF-​L). These regions are split into subregions 
with spatial patterns in the image that are then fed into a neural network to identify 
flaws with good accuracy161. c | Track widths for different powers and speeds are measured 
using a high-​speed camera and the data are used to train a neural network for the PBF-​L 
of stainless steel 316 (left). The width predicted by the neural network agrees with  
the experimental data166 (right). d | The grain growth results (left) from a computationally 
intensive Monte Carlo model provide grain size versus frequency data in two orthogonal 
directions (middle), longitudinal and transverse, that are used to train a neural network 
that could then rapidly calculate grain growth during directed energy deposition using a 
laser heat source (DED-​L) (right)171. e | Temperature data near the fusion zone are measured 
by an infrared camera during DED-​L of Ti–6Al–4V (left) and are correlated with the 
occurrence of porosity using a support vector machine (middle) that can predict porosity 
from the process variables173. CPU, central processing unit. Panel a (printing machine) 
adapted with permission from ref.9, Elsevier. Panel b adapted with permission from ref.161, 
ASME. Panel c adapted with permission from ref.166, Wiley. Panel d adapted from ref.171, 
Springer Nature Limited. Panel e adapted with permission from ref.173, Elsevier.
◀
www.nature.com/natrevmats
Reviews
62 | January 2021 | volume 6	


vision was used to quantify powder characteristics162. 
Machine learning has been used to predict equipment 
failure and proactively anticipate and print replacement 
parts before the actual failure176. In essence, the machine 
learning platform is trained with high-​resolution 
camera imaging and computed tomography scan data, 
and can eventually ‘learn’ to predict problems and detect 
defects in the printing process177. Computer vision 
technology and machine learning are already used in 
industry to perform an inspection of parts and identify 
microscopic cracks in the printed parts to save time 
and money177.
Effective use and impact
The selection of algorithms and the quality and volume 
of data affect the accuracy, reliability and speed of the 
solutions149. For example, a data-​classifying problem 
such as the ‘detected’ or ‘not-​detected’ pores in printed 
metal parts is best addressed by an attribute-​based clas-
sifier algorithm, such as random forest or decision tree, 
rather than a regression-​based neural network147. The 
machine learning literature147 guides the selection of 
algorithms for different classes of problems.
The common issues of data quality, features, imbal-
ance and scarcity can be addressed using data improve-
ments available in the literature149. Not all variables 
in metal printing influence the part attributes equally 
and the selection of input data is important13. Besides, 
the available data need to be checked for reproducibil-
ity and errors. The scarcity of data for the algorithms 
is a common problem13 in AM and data augmentation 
techniques can artificially increase the volume of data148. 
However, duplication of a biased data set for a classifi-
cation problem may lead to poor accuracy of a neural 
network owing to overfitting147. Some algorithms such 
as support vector machines147 can be effective for small 
data sets.
The impact of machine learning may be further 
enhanced by the capabilities of other digital tools, such 
as mechanistic models. For example, the simultane-
ous application of a mechanistic model and machine 
learning in AM has been used in the related field of 
welding178. Peak temperatures, cooling rates, solidi-
fication parameters and other results obtained from 
validated mechanistic models can serve as a source of 
valuable data for machine learning. In dealing with the 
scarcity of data, mechanistic models can provide certain 
features of data or, in some cases, add to the volume of 
data to increase efficiency and reliability of machine 
learning. Such hybrid models may have new capabilities 
beyond improving speed and accuracy.
Research needs
The printing of metallic parts with advanced properties 
and functionality has attracted considerable interest 
in diverse industries. However, AM faces considerable 
scientific, technological and commercial challenges2,179. 
These challenges include the difficulties in controlling 
microstructure, properties and defects, as well as a 
lack of standards, a slow rate of printing, scarcity of 
feedstock materials for many commercial alloys and 
cost-​competitiveness2,11,179.
The scientific challenges originate, to a large extent, 
from the diverse heat input and cooling rates and the 
complex thermal cycles that affect the microstructure, 
properties and defects1,2. The microstructure–property–
performance relationships of many alloys are currently 
being investigated. However, the high dislocation den-
sity, segregation of alloying elements, elongated grains 
and fine microstructural features are complicating fac-
tors for the control of microstructure and properties of 
printed parts. Better understanding of the mechanisms 
for the simultaneous improvements of multiple proper-
ties such as strength and ductility37–41 would enrich sci-
entific understanding of AM and metallurgy. A unified 
approach for the control of solidification morphology 
and texture based on mechanistic models and machine 
learning would accelerate our understanding of texture2. 
Improved theoretical and experimental control of mor-
phology would also benefit the repair of single-​crystal 
turbine blades17. Advanced computational frameworks 
for the control of defects such as lack of fusion, residual 
stresses and distortion will help to reduce defects in parts 
to the levels seen in wrought metal2,180.
Standards are being developed to assist in materials 
and part qualification. Currently, parts are qualified by 
trial and error building and testing of parts2. Predictions 
of solidification structure, grain growth and solid-​state 
phase transformations using mechanistic models before 
printing will be useful to select the parameter space for 
testing and greatly reduce the time and effort needed 
for qualification. Similarly, developing high-​fidelity 
mechanistic models can be helpful for minimizing dis-
tortions and residual stresses prior to building. Models 
of lack of fusion defects are currently being developed to 
avoid conditions for their formation. Multiscale models 
balancing the spatial and temporal resolutions and 
computational efficiencies are needed12.
Machine learning enables the improvement of the 
quality of printed parts by supporting almost every 
step of metal printing, ranging from product design 
to process planning to process monitoring and con-
trol150–154 (Fig. 2). The research needs for machine learn-
ing include the classification and analysis of quality 
data sets to generate training, validation and testing 
sets and the identification of appropriate algorithms181. 
The large data set generated for different combinations 
of AM variants, process parameters and alloys is diffi-
cult to analyse, interpret and classify to train and test 
the machine learning algorithms181,182. Advanced dig-
ital tools and algorithms are needed for data analysis 
and successful implementation of machine learning 
in AM.
The implementation of mechanistic models and 
machine learning in conventional processing is often 
undertaken183 using a digital twin. A digital twin of AM 
can build and test a virtual part prior to building the 
physical one, thus making decisions based on scientific 
principles and data for achieving high-​quality parts. The 
utility of digital twins is well established183 but they are 
not yet generally available for AM. Significant research 
and development are required9,122 to construct or modify 
the building blocks of a digital twin and test them for 
various combinations of alloys and AM processes.
nature Reviews | MAteRiAlS
Reviews
	
 volume 6 | January 2021 | 63


Outlook
The recent growth in sales of commercial AM equip-
ment, the number of patents granted globally and 
the market revenue all point to the expansion of AM 
in the foreseeable future1,2,11,179. The growth of AM in 
niche applications aided by large corporations will 
undoubtedly continue because of the advantages of 
metal printing over conventional processing. However, 
the value of all 3D printed products is now only about 
US$7.3 billion, which is insignificant in comparison 
with the estimated value of US$13 trillion for the global 
manufacturing industry184. Significant expansion of 
AM — more specifically, the printing of many more 
commercial alloys by enterprises of all sizes — will 
depend on our ability to overcome the bottlenecks 
within AM2.
The recent literature on AM points to three unmis-
takable trends. First, the method adapted to solve many 
of the problems faced by AM will not follow the path 
by which technologies matured in the past2. The grow-
ing applications of mechanistic models and machine 
learning to select process parameters will improve part 
quality, lower cost and reduce the volume of trial and 
error experiments for qualifying parts. Second, the 
layer-​by-​layer printing of metals, sometimes with lay-
ers thinner than a human hair, is uncovering puzzling 
scientific issues related to microstructure and proper-
ties2. Multidisciplinary research to solve these problems 
is already advancing the practice of AM and contri­
buting to the science of metallurgy2. Last, 3D printing 
is improving conventional manufacturing. 3D printed 
injection moulds with intricate internal cooling chan-
nels are reducing cooling times and improving pro-
ductivity and part quality; printed milling machine 
tools and heads are extending tool life; 3D printing is 
enabling low-​cost repair of machine tools; and parts 
are additively made and machined in one operation by 
hybrid CNC (computer numerical control) machines 
with 3D printing capability. Thus, the contributions of 
metallurgy, mechanistic models and machine learning 
to metal printing are permeating into conventional 
manufacturing.
In the future, it is likely that metal printing hardware 
will include appropriate electronics to embody and use 
the printability database123,124 to its advantage. Here, a 
printability database can be used to avoid problems such 
as solidification cracking of parts and other defects that 
are persistent problems in AM. For example, a smart 
AM machine can perform preheating of a powder bed 
to avoid part cracking1 in some alloys under certain AM 
conditions. The machine may also progressively update 
process–microstructure–property relations with experi-
ence. Selected mechanistic models can provide guidance 
to select AM parameters to minimize porosity resulting 
from keyhole instability1 and to reduce lack of fusion 
defects185 owing to insufficient overlap of adjacent scan 
paths. Integrating machine learning algorithms with 
the hardware will help to control part geometry and 
make in situ adjustment of process variables to cor-
rect part shape and reduce defects. Such systems will 
collect and use data, control the building process and 
routinely produce reliable parts at low cost with mini-
mal human intervention. The scientific, technological 
and economic challenges faced by metal printing2 will 
be addressed by advances in software and hardware to 
facilitate mechanistic models and machine learning, 
and will continuously improve printability database and 
microstructure–property correlations. These advance-
ments will require worldwide availability of a multidis-
ciplined and technologically orientated workforce to 
integrate these separate fields of expertise into new metal 
printing systems2,9,11.
Published online 2 October 2020
1.	
DebRoy, T. et al. Additive manufacturing of metallic 
components — process, structure and properties.  
Prog. Mater. Sci. 92, 112–224 (2018).
2.	
DebRoy, T. et al. Scientific, technological and economic 
issues in metal printing and their solutions. Nat. Mater. 
18, 1026–1032 (2019).
3.	
Milewski, J. O. Additive Manufacturing of Metals: 
From Fundamental Technology to Rocket Nozzles, 
Medical Implants, and Custom Jewelry Vol. 258 
(Springer, 2017).
4.	
Sames, W. J., List, F. A., Pannala, S., Dehoff, R. R.  
& Babu, S. S. The metallurgy and processing science 
of metal additive manufacturing. Int. Mater. Rev. 61, 
315–360 (2016).
5.	
Bose, S., Ke, D., Sahasrabudhe, H. & Bandyopadhyay, A. 
Additive manufacturing of biomaterials. Prog. Mater. 
Sci. 93, 45–111 (2018).
6.	
Shinde, M. S. & Ashtankar, K. M. Additive 
manufacturing — assisted conformal cooling channels 
in mold manufacturing processes. Adv. Mech. Eng. 9, 
1687814017699764 (2017).
7.	
Qi, D. et al. Mechanical behaviors of SLM additive 
manufactured octet-​truss and truncated-​octahedron 
lattice structures with uniform and taper beams.  
Int. J. Mech. Sci. 163, 105091 (2019).
8.	
Tammas-​Williams, S. & Todd, I. Design for additive 
manufacturing with site-​specific properties in  
metals and alloys. Scr. Mater. 135, 105–110 
(2017).
9.	
Mukherjee, T. & DebRoy, T. A digital twin for rapid 
qualification of 3D printed metallic components.  
Appl. Mater. Today 14, 59–65 (2019).
10.	 Elmer, J. et al. Wire-​based additive manufacturing  
of stainless steel components. Weld. J. 99, S8–S24 
(2020).
11.	 Gao, W. et al. The status, challenges, and future of 
additive manufacturing in engineering. Comput. Aid. 
Des. 69, 65–89 (2015).
12.	 Francois, M. M. et al. Modeling of additive 
manufacturing processes for metals: challenges and 
opportunities. Curr. Opin. Solid State Mater. Sci. 21, 
198–206 (2017).
13.	 Qi, X., Chen, G., Li, Y., Cheng, X. & Li, C. Applying 
neural-​network-based machine learning to additive 
manufacturing: current applications, challenges,  
and future perspectives. Engineering 5, 721–729 
(2019).
14.	 Bürger, D., Parsa, A., Ramsperger, M., Körner, C.  
& Eggeler, G. Creep properties of single crystal Ni-base 
superalloys (SX): a comparison between conventionally 
cast and additive manufactured CMSX-4 materials. 
Mater. Sci. Eng. A 762, 138098 (2019).
15.	 Acharya, R., Bansal, R., Gambone, J. J. & Das, S.  
A coupled thermal, fluid flow, and solidification model 
for the processing of single-​crystal alloy CMSX-4 
through scanning laser epitaxy for turbine engine  
hot-section component repair (Part I). Metall. Mater. 
Trans. B 45, 2247–2261 (2014).
16.	 Acharya, R., Bansal, R., Gambone, J. J. & Das, S.  
A microstructure evolution model for the processing  
of single-​crystal alloy CMSX-4 through scanning laser 
epitaxy for turbine engine hot-​section component 
repair (Part II). Metall. Mater. Trans. B 45, 2279–2290 
(2014).
17.	 Basak, A., Acharya, R. & Das, S. Additive 
manufacturing of single-​crystal superalloy CMSX-4 
through scanning laser epitaxy: computational 
modeling, experimental process development,  
and process parameter optimization. Metall. Mater. 
Trans. A 47, 3845–3859 (2016).
18.	 Liang, Y.-J., Cheng, X., Li, J. & Wang, H.-M. 
Microstructural control during laser additive 
manufacturing of single-​crystal nickel-​base superalloys: 
new processing–microstructure maps involving 
powder feeding. Mater. Des. 130, 197–207 (2017).
19.	 Meid, C. et al. Effect of heat treatment on the high 
temperature fatigue life of single crystalline nickel 
base superalloy additively manufactured by means  
of selective electron beam melting. Scr. Mater. 168, 
124–128 (2019).
20.	 Pistor, J. & Körner, C. Formation of topologically 
closed packed phases within CMSX-4 single crystals 
produced by additive manufacturing. Mater. Lett. X 1, 
100003 (2019).
21.	 Ramsperger, M. et al. Solution heat treatment  
of the single crystal nickel-​base superalloy CMSX-4 
fabricated by selective electron beam melting.  
Adv. Eng. Mater. 17, 1486–1493 (2015).
22.	 Körner, C. et al. Microstructure and mechanical 
properties of CMSX-4 single crystals prepared by 
additive manufacturing. Metall. Mater. Trans. A 49, 
3781–3792 (2018).
23.	 Liang, Y.-J. et al. Experimental optimization of laser 
additive manufacturing process of single-​crystal nickel-​
base superalloys by a statistical experiment design 
method. J. Alloy. Comp. 697, 174–181 (2017).
24.	 Butler, T. M., Brice, C. A., Tayon, W. A., Semiatin, S. L. 
& Pilchak, A. L. Evolution of texture from a single 
crystal Ti–6Al–4V substrate during electron beam 
directed energy deposition. Metall. Mater. Trans. A 
48, 4441–4446 (2017).
25.	 Zhou, Z. et al. Causes analysis on cracks in nickel-​
based single crystal superalloy fabricated by laser 
powder deposition additive manufacturing. Mater. Des. 
160, 1238–1249 (2018).
www.nature.com/natrevmats
Reviews
64 | January 2021 | volume 6	


26.	 Wei, H. L., Elmer, J. W. & DebRoy, T. Three-​
dimensional modeling of grain structure evolution 
during welding of an aluminum alloy. Acta Mater. 126, 
413–425 (2017).
27.	 MacDonald, E. & Wicker, R. Multiprocess 3D printing 
for increasing component functionality. Science 353, 
aaf2093 (2016).
28.	 Niendorf, T. et al. Functionally graded alloys obtained 
by additive manufacturing. Adv. Eng. Mater. 16,  
857–861 (2014).
29.	 Bobbio, L. D. et al. Analysis of formation and growth 
of the σ phase in additively manufactured functionally 
graded materials. J. Alloy. Comp. 814, 151729 
(2020).
30.	 Zuback, J., Palmer, T. & DebRoy, T. Additive 
manufacturing of functionally graded transition joints 
between ferritic and austenitic alloys. J. Alloy. Comp. 
770, 995–1003 (2019).
31.	 Ge, W., Lin, F. & Guo, C. in Proc. 26th Annu. Int. Solid 
Freeform Fabrication Symp. — An Addit. Manuf. Conf. 
(eds Bourell, D. L., Crawford, R.H., Seepersad, C. C., 
Beaman, J., J., Fish, S. & Marcus, H.) 10–12  
(The University of Texas, Austin, 2015).
32.	 Wang, F., Mei, J., Jiang, H. & Wu, X. H. Production  
of functionally-​graded samples using simultaneous 
powder and wire-​feed. Mater. Sci. Forum. 539,  
3631–3636 (2007).
33.	 Hofmann, D. C. et al. Developing gradient metal alloys 
through radial deposition additive manufacturing.  
Sci. Rep. 4, 5357 (2014).
34.	 Bobbio, L. D. et al. Additive manufacturing of a 
functionally graded material from Ti–6Al–4V to Invar: 
experimental characterization and thermodynamic 
calculations. Acta Mater. 127, 133–142 (2017).
35.	 Gan, Z., Yu, G., He, X. & Li, S. Numerical simulation  
of thermal behavior and multicomponent mass 
transfer in direct laser deposition of Co-​base alloy  
on steel. Int. J. Heat Mass Transf. 104, 28–38 
(2017).
36.	 Eliseeva, O. et al. Functionally graded materials 
through robotics-​inspired path planning. Mater. Des. 
182, 107975 (2019).
37.	 Wang, Y. M. et al. Additively manufactured hierarchical 
stainless steels with high strength and ductility. Nat. 
Mater. 17, 63 (2018).
38.	 Yin, Y., Sun, J., Guo, J., Kan, X. & Yang, D. Mechanism 
of high yield strength and yield ratio of 316 L stainless 
steel by additive manufacturing. Mater. Sci. Eng. A 
744, 773–777 (2019).
39.	 Liu, L. et al. Dislocation network in additive 
manufactured steel breaks strength–ductility 
trade-off. Mater. Today 21, 354–361 (2018).
40.	 Sun, Z., Tan, X., Tor, S. B. & Chua, C. K. Simultaneously 
enhanced strength and ductility for 3D-​printed 
stainless steel 316L by selective laser melting.  
NPG Asia Mater. 10, 127 (2018).
41.	 Pham, M., Dovgyy, B. & Hooper, P. Twinning induced 
plasticity in austenitic stainless steel 316L made  
by additive manufacturing. Mater. Sci. Eng. A 704, 
102–111 (2017).
42.	 Wang, D. et al. Selective laser melting under the 
reactive atmosphere: a convenient and efficient 
approach to fabricate ultrahigh strength commercially 
pure titanium without sacrificing ductility. Mater. Sci. 
Eng. A. 762, 138078 (2019).
43.	 Zhou, Y. et al. Selective laser melting enabled additive 
manufacturing of Ti–22Al–25Nb intermetallic: 
excellent combination of strength and ductility,  
and unique microstructural features associated.  
Acta Mater. 173, 117–129 (2019).
44.	 Lin, J. et al. Enhanced strength and ductility in thin 
Ti–6Al–4V alloy components by alternating the 
thermal cycle strategy during plasma arc additive 
manufacturing. Mater. Sci. Eng. A 759, 288–297 
(2019).
45.	 De Formanoir, C. et al. Micromechanical behavior and 
thermal stability of a dual-​phase α + α′ titanium alloy 
produced by additive manufacturing. Acta Mater. 
162, 149–162 (2019).
46.	 Sabban, R., Bahl, S., Chatterjee, K. & Suwas, S. 
Globularization using heat treatment in additively 
manufactured Ti–6Al–4V for high strength and 
toughness. Acta Mater. 162, 239–254 (2019).
47.	 Azizi, H. et al. Additive manufacturing of a novel  
Ti–Al–V–Fe alloy using selective laser melting.  
Addit. Manuf. 21, 529–535 (2018).
48.	 He, B. et al. Microstructural characteristic and 
mechanical property of Ti6Al4V alloy fabricated  
by selective laser melting. Vacuum 150, 79–83 
(2018).
49.	 AlMangour, B., Kim, Y.-K., Grzesiak, D. & Lee, K.-A. 
Novel TiB2-reinforced 316L stainless steel nano­
composites with excellent room- and high-​temperature 
yield strength developed by additive manufacturing. 
Compos. Part. B Eng. 156, 51–63 (2019).
50.	 Dong, Z., Kang, H., Xie, Y., Chi, C. & Peng, X. Effect  
of powder oxygen content on microstructure and 
mechanical properties of a laser additively-​
manufactured 12CrNi2 alloy steel. Mater. Lett. 236, 
214–217 (2019).
51.	 Suryawanshi, J. et al. Simultaneous enhancements  
of strength and toughness in an Al–12Si alloy 
synthesized using selective laser melting. Acta Mater. 
115, 285–294 (2016).
52.	 Wang, Z., Palmer, T. A. & Beese, A. M. Effect of 
processing parameters on microstructure and tensile 
properties of austenitic stainless steel 304L made by 
directed energy deposition additive manufacturing. 
Acta Mater. 110, 226–235 (2016).
53.	 Dadbakhsh, S., Mertens, R., Hao, L., Van Humbeeck, J. 
& Kruth, J. P. Selective laser melting to manufacture 
“in situ” metal matrix composites: a review. Adv. Eng. 
Mater. 21, 1801244 (2019).
54.	 Wang, Y., Shi, J., Deng, X. & Lu, S. in ASME 2016 
International Mechanical Engineering Congress and 
Exposition https://doi.org/10.1115/IMECE2016-
67304 (American Society of Mechanical Engineers 
Digital Collection, 2016).
55.	 Gu, D. et al. Laser additive manufacturing of nano-​TiC 
reinforced Ni-​based nanocomposites with tailored 
microstructure and performance. Compos. Part. B 
Eng. 163, 585–597 (2019).
56.	 Gu, D., Cao, S. & Lin, K. Laser metal deposition 
additive manufacturing of TiC reinforced Inconel 625 
composites: influence of the additive TiC particle and 
its starting size. J. Manuf. Sci. Eng. 139, 041014 
(2017).
57.	 Zhang, B. et al. Comparison of carbon-​based 
reinforcement on laser aided additive manufacturing 
Inconel 625 composites. Appl. Surf. Sci. 490,  
522–534 (2019).
58.	 Li, X. P. et al. Selective laser melting of nano-​TiB2 
decorated AlSi10Mg alloy with high fracture strength 
and ductility. Acta Mater. 129, 183–193 (2017).
59.	 Zhou, W. et al. In situ formation of uniformly dispersed 
Al4C3 nanorods during additive manufacturing of 
graphene oxide/Al mixed powders. Carbon. 141, 
67–75 (2019).
60.	 Du, Z., Tan, M. J., Guo, J. F., Chua, C. K. & Lim, J. J. D. 
The effect of laser power and scanning speed on the 
density of selective laser melting fabricated Al–CNT 
composites. DR-​NTU https://hdl.handle.net/ 
10356/84568 (Research Publishing, 2016).
61.	 Mereddy, S. et al. Trace carbon addition to refine 
micro­structure and enhance properties of additive-​
manufactured Ti–6Al–4V. JOM 70, 1670–1676 
(2018).
62.	 Yu, W., Sing, S., Chua, C., Kuo, C. & Tian, X. Particle-​
reinforced metal matrix nanocomposites fabricated  
by selective laser melting: a state of the art review. 
Prog. Mater. Sci. 104, 330–379 (2019).
63.	 Wei, H. L., Knapp, G. L., Mukherjee, T. & DebRoy, T. 
Three-​dimensional grain growth during multi-​layer 
printing of a nickel-​based alloy Inconel 718. Addit. 
Manuf. 25, 448–459 (2019).
64.	 Jadhav, S. et al. Influence of selective laser melting 
process parameters on texture evolution in pure 
copper. J. Mater. Process. Tech. 270, 47–58 (2019).
65.	 Andreau, O. et al. Texture control of 316L parts by 
modulation of the melt pool morphology in selective 
laser melting. J. Mater. Process. Tech. 264, 21–31 
(2019).
66.	 Martin, J. H. et al. 3D printing of high-​strength 
aluminium alloys. Nature 549, 365 (2017).
67.	 Wen, X. et al. Laser solid forming additive 
manufacturing TiB2 reinforced 2024Al composite: 
microstructure and mechanical properties. Mater. Sci. 
Eng. A 745, 319–325 (2019).
68.	 Bermingham, M. J., StJohn, D. H., Krynen, J., 
Tedman-​Jones, S. & Dargusch, M. S. Promoting the 
columnar to equiaxed transition and grain refinement 
of titanium alloys during additive manufacturing.  
Acta Mater. 168, 261–274 (2019).
69.	 Li, J. et al. Microstructures and mechanical properties 
of laser additive manufactured Al–5Si–1Cu–Mg alloy 
with different layer thicknesses. J. Alloy. Comp. 789, 
15–24 (2019).
70.	 Helmer, H., Bauereiß, A., Singer, R. & Körner, C.  
Grain structure evolution in Inconel 718 during 
selective electron beam melting. Mater. Sci. Eng. A 
668, 180–187 (2016).
71.	 Haines, M., Plotkowski, A., Frederick, C., Schwalbach, E. 
& Babu, S. S. A sensitivity analysis of the columnar-​
to-equiaxed transition for Ni-​based superalloys in 
electron beam additive manufacturing. Comp. Mater. 
Sci. 155, 340–349 (2018).
72.	 Raghavan, N. et al. Localized melt-​scan strategy for 
site specific control of grain size and primary dendrite 
arm spacing in electron beam additive manufacturing. 
Acta Mater. 140, 375–387 (2017).
73.	 Jia, Q. et al. Selective laser melting of a high strength 
AlMnSc alloy: alloy design and strengthening 
mechanisms. Acta Mater. 171, 108–118 (2019).
74.	 Todaro, C. J. et al. Grain structure control during  
metal 3D printing by high-​intensity ultrasound.  
Nat. Commun. 11, 142 (2020).
75.	 Lee, H. W., Jung, K.-H., Hwang, S.-K., Kang, S.-H.  
& Kim, D.-K. Microstructure and mechanical 
anisotropy of CoCrW alloy processed by selective  
laser melting. Mater. Sci. Eng. A 749, 65–73 (2019).
76.	 Bahl, S. et al. Non-​equilibrium microstructure, 
crystallographic texture and morphological texture 
synergistically result in unusual mechanical properties 
of 3D printed 316L stainless steel. Addit. Manuf. 28, 
65–77 (2019).
77.	 Gordon, J., Hochhalter, J., Haden, C. & Harlow, D. G. 
Enhancement in fatigue performance of metastable 
austenitic stainless steel through directed energy 
deposition additive manufacturing. Mater. Des. 168, 
107630 (2019).
78.	 Tarasov, S. Y. et al. Microstructural evolution and 
chemical corrosion of electron beam wire-​feed 
additively manufactured AISI 304 stainless steel.  
J. Alloy. Comp. 803, 364–370 (2019).
79.	 Du, D. et al. Influence of build orientation on 
microstructure, mechanical and corrosion behavior  
of Inconel 718 processed by selective laser melting. 
Mater. Sci. Eng. A 760, 469–480 (2019).
80.	 Wang, L. Y., Zhou, Z. J., Li, C. P., Chen, G. F.  
& Zhang, G. P. Comparative investigation of small 
punch creep resistance of Inconel 718 fabricated by 
selective laser melting. Mater. Sci. Eng. A 745, 31–38 
(2019).
81.	 Dinda, G., Dasgupta, A. & Mazumder, J. Texture 
control during laser deposition of nickel-​based 
superalloy. Scr. Mater. 67, 503–506 (2012).
82.	 Wei, H. L., Mazumder, J. & DebRoy, T. Evolution of 
solidification texture during additive manufacturing. 
Sci. Rep. 5, 16446 (2015).
83.	 Carlton, H. D., Klein, K. D. & Elmer, J. W. Evolution of 
microstructure and mechanical properties of selective 
laser melted Ti–5Al–5V–5Mo–3Cr after heat 
treatments. Sci. Technol. Weld. Join. 24, 465–473 
(2019).
84.	 Thijs, L., Kempen, K., Kruth, J. P. & Van Humbeeck, J. 
Fine-​structured aluminium products with controllable 
texture by selective laser melting of pre-​alloyed 
AlSi10Mg powder. Acta Mater. 61, 1809–1819 
(2013).
85.	 Garibaldi, M., Ashcroft, I., Simonelli, M. & Hague, R. 
Metallurgy of high-​silicon steel parts produced using 
selective laser melting. Acta Mater. 110, 207–216 
(2016).
86.	 Antonysamy, A. A., Meyer, J. & Prangnell, P. B. Effect 
of build geometry on the β-​grain structure and texture 
in additive manufacture of Ti6Al4V by selective 
electron beam melting. Mater. Charact. 84, 153–168 
(2013).
87.	 Ocelík, V., Furár, I. & De Hosson, J. T. M. 
Microstructure and properties of laser clad coatings 
studied by orientation imaging microscopy. Acta Mater. 
58, 6763–6772 (2010).
88.	 Bhattacharya, S., Dinda, G. P., Dasgupta, A. K.  
& Mazumder, J. A comparative study of 
microstructure and mechanical behavior of CO2 and 
diode laser deposited Cu–38Ni alloy. J. Mater. Sci. 
49, 2415–2429 (2014).
89.	 Dinda, G. P., Dasgupta, A. K. & Mazumder, J. 
Evolution of microstructure in laser deposited 
Al–11.28%Si alloy. Surf. Coat. Tech. 206, 2152–2160 
(2012).
90.	 Kontis, P. et al. Atomic-​scale grain boundary 
engineering to overcome hot-​cracking in additively-​
manufactured superalloys. Acta Mater. 177,  
209–221 (2019).
91.	 Dryburgh, P. et al. Spatially resolved acoustic 
spectroscopy for integrity assessment in wire–arc 
additive manufacturing. Addit. Manuf. 28, 236–251 
(2019).
92.	 Patel, R. et al. Imaging material texture of as-​deposited 
selective laser melted parts using spatially resolved 
acoustic spectroscopy. Appl. Sci. 8, 1991 (2018).
93.	 Everton, S. K., Hirsch, M., Stravroulakis, P., Leach, R. K. 
& Clare, A. T. Review of in-​situ process monitoring and 
in-​situ metrology for metal additive manufacturing. 
Mater. Des. 95, 431–445 (2016).
nature Reviews | MAteRiAlS
Reviews
	
 volume 6 | January 2021 | 65


94.	 Koepf, J. A., Gotterbarm, M. R., Markl, M. & Körner, C. 
3D multi-​layer grain structure simulation of powder 
bed fusion additive manufacturing. Acta Mater. 152, 
119–126 (2018).
95.	 Coeck, S., Bisht, M., Plas, J. & Verbist, F. Prediction of 
lack of fusion porosity in selective laser melting based 
on melt pool monitoring data. Addit. Manuf. 25, 
347–356 (2019).
96.	 Mukherjee, T., Zuback, J. S., Zhang, W. & DebRoy, T. 
Residual stresses and distortion in additively 
manufactured compositionally graded and dissimilar 
joints. Comp. Mater. Sci. 143, 325–337 (2018).
97.	 Cunningham, R. et al. Keyhole threshold and 
morphology in laser melting revealed by 
ultrahigh-speed X-​ray imaging. Science 363,  
849–852 (2019).
98.	 Martin, A. A. et al. Dynamics of pore formation during 
laser powder bed fusion additive manufacturing.  
Nat. Commun. 10, 1987 (2019).
99.	 Ge, J. et al. Wire-​arc additive manufacturing H13 part: 
3D pore distribution, microstructural evolution, and 
mechanical performances. J. Alloy. Comp. 783,  
145–155 (2019).
100.	Yu, W., Sing, S. L., Chua, C. K. & Tian, X. Influence  
of re-​melting on surface roughness and porosity of 
AlSi10Mg parts fabricated by selective laser melting. 
J. Alloy. Comp. 792, 574–581 (2019).
101.	Leung, C. L. A. et al. The effect of powder oxidation  
on defect formation in laser additive manufacturing. 
Acta Mater. 166, 294–305 (2019).
102.	Tillmann, W. et al. Hot isostatic pressing of IN718 
components manufactured by selective laser melting. 
Addit. Manuf. 13, 93–102 (2017).
103.	AlMangour, B., Grzesiak, D. & Yang, J.-M. Selective 
laser melting of TiB2/H13 steel nanocomposites: 
influence of hot isostatic pressing post-​treatment.  
J. Mater. Process. Technol. 244, 344–353 (2017).
104.	Khomutov, M. et al. Effect of hot isostatic pressing on 
structure and properties of intermetallic NiAl–Cr–Mo 
alloy produced by selective laser melting. Intermetallics 
120, 106766 (2020).
105.	Kou, S. A criterion for cracking during solidification. 
Acta Mater. 88, 366–374 (2015).
106.	Withers, P. J. & Bhadeshia, H. Residual stress.  
Part 2—nature and origins. Mater. Sci. Technol. 17, 
366–375 (2001).
107.	Levkulich, N. C. et al. The effect of process parameters 
on residual stress evolution and distortion in the laser 
powder bed fusion of Ti–6Al–4V. Addit. Manuf. 28, 
475–484 (2019).
108.	Onuike, B. & Bandyopadhyay, A. Additive 
manufacturing of Inconel 718–Ti6Al4V bimetallic 
structures. Addit. Manuf. 22, 844–851 (2018).
109.	Li, C., Liu, Z. Y., Fang, X. Y. & Guo, Y. B. Residual stress 
in metal additive manufacturing. Procedia CIRP 71, 
348–353 (2018).
110.	 Lu, X. et al. Residual stress and distortion of 
rectangular and S-​shaped Ti–6Al–4V parts by directed 
energy deposition: modelling and experimental 
calibration. Addit. Manuf. 26, 166–179 (2019).
111.	 Tyagi, P. et al. Reducing the roughness of internal 
surface of an additive manufacturing produced 316 
steel component by chempolishing and electropolishing. 
Addit. Manuf. 25, 32–38 (2019).
112.	Bhaduri, D. et al. Evaluation of surface/interface 
quality, microstructure and mechanical properties  
of hybrid additive–subtractive aluminium parts.  
CIRP Ann. 68, 237–240 (2019).
113.	Yang, T. et al. The influence of process parameters  
on vertical surface roughness of the AlSi10Mg parts 
fabricated by selective laser melting. J. Mater. 
Process. Technol. 266, 26–36 (2019).
114.	Chen, Z., Wu, X., Tomus, D. & Davies, C. H. J. Surface 
roughness of selective laser melted Ti–6Al–4V alloy 
components. Addit. Manuf. 21, 91–103 (2018).
115.	Derekar, K. S. A review of wire arc additive 
manufacturing and advances in wire arc additive 
manufacturing of aluminium. Mater. Sci. Technol. 34, 
895–916 (2018).
116.	Ali, U. et al. Identification and characterization of 
spatter particles and their effect on surface roughness, 
density and mechanical response of 17-4 PH stainless 
steel laser powder-​bed fusion parts. Mater. Sci. Eng. A 
756, 98–107 (2019).
117.	Cao, L. Numerical simulation of the impact of laying 
powder on selective laser melting single-​pass formation. 
Int. J. Heat Mass Transf. 141, 1036–1048 (2019).
118.	Manvatkar, V., De, A. & DebRoy, T. Heat transfer and 
material flow during laser assisted multi-​layer additive 
manufacturing. J. Appl. Phys. 116, 124905 (2014).
119.	Mukherjee, T., Wei, H. L., De, A. & DebRoy, T. Heat 
and fluid flow in additive manufacturing — Part I: 
modeling of powder bed fusion. Comput. Mater. Sci. 
150, 304–313 (2018).
120.	Ou, W., Mukherjee, T., Knapp, G. L., Wei, Y. &  
DebRoy, T. Fusion zone geometries, cooling rates  
and solidification parameters during wire arc additive 
manufacturing. Int. J. Heat Mass Transf. 127,  
1084–1094 (2018).
121.	Mukherjee, T., Wei, H. L., De, A. & DebRoy, T. Heat 
and fluid flow in additive manufacturing — Part II: 
powder bed fusion of stainless steel, and titanium, 
nickel and aluminum base alloys. Comput. Mater. Sci. 
150, 369–380 (2018).
122.	Knapp, G. L. et al. Building blocks for a digital twin of 
additive manufacturing. Acta Mater. 135, 390–399 
(2017).
123.	Mukherjee, T. & DebRoy, T. Printability of 316 
stainless steel. Sci. Technol. Weld. Join. 24, 412–419 
(2019).
124.	Mukherjee, T., Zuback, J. S., De, A. & DebRoy, T. 
Printability of alloys for additive manufacturing.  
Sci. Rep. 6, 19717 (2016).
125.	Tan, J. H. K., Sing, S. L. & Yeong, W. Y. Microstructure 
modelling for metallic additive manufacturing:  
a review. Virtual Phys. Prototyp. 15, 87–105 (2020).
126.	Bhadeshia, H., Svensson, L.-E. & Gretoft, B. A model 
for the development of microstructure in low-​alloy 
steel (Fe–Mn–Si–C) weld deposits. Acta Metall. 33, 
1271–1283 (1985).
127.	Li, X. & Tan, W. Numerical investigation of effects of 
nucleation mechanisms on grain structure in metal 
additive manufacturing. Comput. Mater. Sci. 153, 
159–169 (2018).
128.	Nie, P., Ojo, O. A. & Li, Z. Numerical modeling  
of microstructure evolution during laser additive 
manufacturing of a nickel-​based superalloy. Acta Mater. 
77, 85–95 (2014).
129.	Yang, Y., Jamshidinia, M., Boulware, P. & Kelly, S. 
Prediction of microstructure, residual stress, and 
deformation in laser powder bed fusion process. 
Comput. Mech. 61, 599–615 (2018).
130.	Baykasoglu, C., Akyildiz, O., Candemir, D., Yang, Q.  
& To, A. C. Predicting microstructure evolution during 
directed energy deposition additive manufacturing  
of Ti–6Al–4V. J. Manuf. Sci. Eng. 140, 051003 
(2018).
131.	Sui, S. et al. The influence of Laves phases on the 
room temperature tensile properties of Inconel  
718 fabricated by powder feeding laser additive 
manufacturing. Acta Mater. 164, 413–427 (2019).
132.	Qin, R. & Bhadeshia, H. Phase field method. Mater. 
Sci. Technol. 26, 803–811 (2010).
133.	Zheng, W. et al. Phase field investigation of dendrite 
growth in the welding pool of aluminum alloy 2A14 
under transient conditions. Comput. Mater. Sci. 82, 
525–530 (2014).
134.	Keller, T. et al. Application of finite element,  
phase-​field, and CALPHAD-​based methods to additive 
manufacturing of Ni-​based superalloys. Acta Mater. 
139, 244–253 (2017).
135.	Shi, R. et al. Integrated simulation framework for 
additively manufactured Ti–6Al–4V: melt pool 
dynamics, microstructure, solid-​state phase 
transformation, and microelastic response. JOM 71, 
3640–3655 (2019).
136.	Lian, Y., Lin, S., Yan, W., Liu, W. K. & Wagner, G. J.  
A parallelized three-​dimensional cellular automaton 
model for grain growth during additive manufacturing. 
Comput. Mech. 61, 543–558 (2018).
137.	Rodgers, T. M., Madison, J. D. & Tikare, V. Simulation 
of metal additive manufacturing microstructures using 
kinetic Monte Carlo. Comput. Mater. Sci. 135, 78–89 
(2017).
138.	Mukherjee, T., Zhang, W. & DebRoy, T. An improved 
prediction of residual stresses and distortion in 
additive manufacturing. Comput. Mater. Sci. 126, 
360–372 (2017).
139.	Mukherjee, T., Manvatkar, V., De, A. & DebRoy, T. 
Mitigation of thermal distortion during additive 
manufacturing. Scr. Mater. 127, 79–83 (2017).
140.	Wang, Z., Yan, W., Liu, W. K. & Liu, M.  
Powder-​scale multi-​physics modeling of multi-​layer 
multi-​track selective laser melting with sharp interface 
capturing method. Comput. Mech. 63, 649–661 
(2019).
141.	Lee, Y. & Zhang, W. Modeling of heat transfer, fluid 
flow and solidification microstructure of nickel-​base 
superalloy fabricated by laser powder bed fusion. 
Addit. Manuf. 12, 178–188 (2016).
142.	Tang, C., Tan, J. L. & Wong, C. H. A numerical 
investigation on the physical mechanisms of single 
track defects in selective laser melting. Int. J. Heat 
Mass Transf. 126, 957–968 (2018).
143.	Khairallah, S. A., Anderson, A. T., Rubenchik, A.  
& King, W. E. Laser powder-​bed fusion additive 
manufacturing: physics of complex melt flow and 
formation mechanisms of pores, spatter, and 
denudation zones. Acta Mater. 108, 36–45 (2016).
144.	Knoll, H. et al. Combinatorial alloy design by laser 
additive manufacturing. Steel Res. Int. 88, 1600416 
(2017).
145.	Schwendner, K. I., Banerjee, R., Collins, P. C., Brice, C. A. 
& Fraser, H. L. Direct laser deposition of alloys from 
elemental powder blends. Scr. Mater. 45, 1123–1129 
(2001).
146.	Aversa, A. et al. New aluminum alloys specifically 
designed for laser powder bed fusion: a review. 
Materials 12, 1007 (2019).
147.	Mitchell, T. M. Machine Learning (McGraw-​Hill, 1997).
148.	LeCun, Y., Bengio, Y. & Hinton, G. Deep learning. 
Nature 521, 436–444 (2015).
149.	Jordan, M. I. & Mitchell, T. M. Machine learning: 
trends, perspectives, and prospects. Science 349, 
255–260 (2015).
150.	Zhang, B., Jaiswal, P., Rai, R., Guerrier, P. & Baggs, G. 
Convolutional neural network-​based inspection of 
metal additive manufacturing parts. Rapid Prototyp. J. 
25, 530–540 (2019).
151.	Aoyagi, K., Wang, H., Sudo, H. & Chiba, A. Simple 
method to construct process maps for additive 
manufacturing using a support vector machine.  
Addit. Manuf. 27, 353–362 (2019).
152.	Wang, Y., Blache, R., Zheng, P. & Xu, X. A knowledge 
management system to support design for additive 
manufacturing using Bayesian networks. J. Mech. Des. 
140, 051701 (2018).
153.	Wu, D., Wei, Y. & Terpenny, J. Predictive modelling of 
surface roughness in fused deposition modelling using 
data fusion. Int. J. Prod. Res. 57, 3992–4006 (2019).
154.	Zhao, Z., Guo, Y., Bai, L., Wang, K. & Han, J. Quality 
monitoring in wire-​arc additive manufacturing based 
on cooperative awareness of spectrum and vision. 
Optik 181, 351–360 (2019).
155.	Du, Y., Mukherjee, T. & DebRoy, T. Conditions for  
void formation in friction stir welding from machine 
learning. NPJ Comput. Mater. 5, 68 (2019).
156.	Xiong, J., Zhang, G., Hu, J. & Wu, L. Bead geometry 
prediction for robotic GMAW-​based rapid 
manufacturing through a neural network and a 
second-​order regression analysis. J. Intell. Manuf. 25, 
157–163 (2014).
157.	Ding, D. et al. Towards an automated robotic  
arc-​welding-based additive manufacturing system  
from CAD to finished part. Comput. Aid. Des. 73, 
66–75 (2016).
158.	Kappes, B., Moorthy, S., Drake, D., Geerlings, H. & 
Stebner, A. in Proc. 9th Int. Symp. on Superalloy 718 
& Derivatives: Energy, Aerospace, and Industrial 
Applications (eds Ott, E., Liu, X., Andersson, J., Bi, Z., 
Bockenstedt, K., Dempster, I., Groh, J., Heck, K., 
Jablonski, P., Kaplan, M., Nagahama, D. &  
Sudbrack, C.) 595–610 (Springer, 2018).
159.	Zhang, W., Mehta, A., Desai, P. S. & Higgs, C. in Int. 
Solid Freeform Fabrication Symp. (eds Bourell, D. L., 
Crawford, R. H., Seepersad, C. C., Beaman, J. J. & 
Fish, S.) 1235–1249 (The University of Texas, Austin, 
2017).
160.	Rosa, B., Mognol, P. & Hascoët, J.-Y. Modelling  
and optimization of laser polishing of additive laser 
manufacturing surfaces. Rapid Prototyp. J. 22,  
956–964 (2016).
161.	Imani, F., Chen, R., Diewald, E., Reutzel, E. & Yang, H. 
Deep learning of variant geometry in layerwise 
imaging profiles for additive manufacturing quality 
control. J. Manuf. Sci. Eng. 141, 111001 (2019).
162.	DeCost, B. L., Jain, H., Rollett, A. D. & Holm, E. A. 
Computer vision and machine learning for autonomous 
characterization of AM powder feedstocks. JOM 69, 
456–465 (2017).
163.	Amini, M. & Chang, S. I. MLCPM: a process monitoring 
framework for 3D metal printing in industrial scale. 
Comput. Ind. Eng. 124, 322–330 (2018).
164.	Mazumder, J. Design for metallic additive 
manufacturing machine with capability for “Certify as 
You Build”. Procedia CIRP 36, 187–192 (2015).
165.	Wu, Q., Mukherjee, T., Liu, C., Lu, J. & DebRoy, T. 
Residual stresses and distortion in the patterned 
printing of titanium and nickel alloys. Addit. Manuf. 
29, 100808 (2019).
166.	Yuan, B. et al. Machine-​learning-based monitoring  
of laser powder bed fusion. Adv. Mater. Technol. 3, 
1800136 (2018).
167.	Caiazzo, F. & Caggiano, A. Laser direct metal 
deposition of 2024 Al alloy: trace geometry prediction 
via machine learning. Materials 11, 444 (2018).
www.nature.com/natrevmats
Reviews
66 | January 2021 | volume 6	


168.	Kamath, C. Data mining and statistical inference in 
selective laser melting. Int. J. Adv. Manuf. Technol. 86, 
1659–1677 (2016).
169.	Zhu, Z., Anwer, N., Huang, Q. & Mathieu, L. Machine 
learning in tolerancing for additive manufacturing. 
CIRP Ann. 67, 157–160 (2018).
170.	Wan, H., Chen, G., Li, C., Qi, X. & Zhang, G. Data-​
driven evaluation of fatigue performance of additive 
manufactured parts using miniature specimens.  
J. Mater. Sci. Technol. 35, 1137–1146 (2019).
171.	Popova, E. et al. Process-​structure linkages using  
a data science approach: application to simulated 
additive manufacturing data. Integr. Mater. Manuf. 
Innov. 6, 54–68 (2017).
172.	Collins, P. C. et al. Progress toward an integration of 
process–structure–property–performance models for 
“three-​dimensional (3-D) printing” of titanium alloys. 
JOM 66, 1299–1309 (2014).
173.	Khanzadeh, M., Chowdhury, S., Marufuzzaman, M., 
Tschopp, M. A. & Bian, L. Porosity prediction: 
supervised-​learning of thermal history for direct laser 
deposition. J. Manuf. Syst. 47, 69–82 (2018).
174.	Scime, L. & Beuth, J. A multi-​scale convolutional 
neural network for autonomous anomaly detection 
and classification in a laser powder bed fusion additive 
manufacturing process. Addit. Manuf. 24, 273–286 
(2018).
175.	Scime, L. & Beuth, J. Anomaly detection and 
classification in a laser powder bed additive 
manufacturing process using a trained computer 
vision algorithm. Addit. Manuf. 19, 114–126 (2018).
176.	Bharadwaj, R. Artificial intelligence applications in 
additive manufacturing (3D printing). Emerj — Artificial 
Intelligence Research and Insight https://emerj.com/ 
ai-​sector-overviews/artificial-​intelligence-applications-​
additive-manufacturing-3d-​printing/ (2019).
177.	Ali, A. B. Deep learning for advanced additive 
manufacturing. Medium https://medium.com/ 
@amynebenali/deep-​learning-for-​advanced-additive-​
manufacturing-65157e7a1b06 (2018).
178.	Du, Y., Mukherjee, T., Mitra, P. & DebRoy, T. Machine 
learning based hierarchy of causative variables for tool 
failure in friction stir welding. Acta Mater. 192, 
67–77 (2020).
179.	Tofail, S. A. et al. Additive manufacturing: scientific 
and technological challenges, market uptake and 
opportunities. Mater. Today 21, 22–37 (2018).
180.	Johnson, L. et al. Assessing printability maps in 
additive manufacturing of metal alloys. Acta Mater. 
176, 199–210 (2019).
181.	Huang, D. J. & Li, H. in Proc. 3rd Int. Conf. Progress 
Addit. Manuf. (eds, Chua, C. K, Yeong, W. Y., Tan, M. 
J., Liu, E. & Tor, S. B.) (Pro-AM, 2018).
182.	Li, B.-h, Hou, B.-c, Yu, W.-t, Lu, X.-b & Yang, C.-w. 
Applications of artificial intelligence in intelligent 
manufacturing: a review. Front. Inf. Technol. Electron. 
Eng. 18, 86–96 (2017).
183.	Qi, Q. & Tao, F. Digital twin and big data towards 
smart manufacturing and industry 4.0: 360 degree 
comparison. IEEE Access. 6, 3585–3593 (2018).
184.	Wohlers, T., Caffrey, T., Campbell, R. I., Diegel, O.  
& Kowen, J. Wohlers Report 2018: 3D Printing and 
Additive Manufacturing State of the Industry; Annual 
Worldwide Progress Report (Wohlers Associates, 2018).
185.	Mukherjee, T. & DebRoy, T. Mitigation of lack of fusion 
defects in powder bed fusion additive manufacturing. 
J. Manuf. Process. 36, 442–449 (2018).
186.	3DscienceValley. Digital Alloys’ guide to metal additive 
manufacturing — Part 13, Joule Printing™ vs wire 
DED. Digital Alloys https://www.digitalalloys.com/blog/ 
joule-​printing-vs-​wire-ded (2019).
187.	Donoghue, J. et al. The effectiveness of combining 
rolling deformation with wire–arc additive 
manufacture on β-​grain refinement and texture 
modification in Ti–6Al–4V. Mater. Charact. 114, 
103–114 (2016).
188.	Majeed, M., Khan, H. & Rasheed, I. Finite element 
analysis of melt pool thermal characteristics with 
passing laser in SLM process. Optik 194, 163068 
(2019).
189.	Khan, K. & De, A. Modelling of selective laser melting 
process with adaptive remeshing. Sci. Technol. Weld. 
Join. 24, 391–400 (2019).
190.	Huang, Y. et al. Rapid prediction of real-​time thermal 
characteristics, solidification parameters and 
microstructure in laser directed energy deposition 
(powder-​fed additive manufacturing). J. Mater. 
Process. Technol. 274, 116286 (2019).
191.	Bai, X. et al. Numerical analysis of heat transfer and 
fluid flow in multilayer deposition of PAW-​based wire 
and arc additive manufacturing. Int. J. Heat Mass 
Transf. 124, 504–516 (2018).
192.	He, X. & Mazumder, J. Transport phenomena during 
direct metal deposition. J. Appl. Phys. 101, 053113 
(2007).
193.	Klassen, A., Scharowsky, T. & Körner, C. Evaporation 
model for beam based additive manufacturing using 
free surface lattice Boltzmann methods. J. Phys. D. 
Appl. Phys. 47, 275303 (2014).
194.	Rausch, A. M., Markl, M. & Körner, C. Predictive 
simulation of process windows for powder bed fusion 
additive manufacturing: influence of the powder size 
distribution. Comput. Math. Appl. 78, 2351–2359 
(2019).
195.	Lindwall, G. et al. Simulation of TTT curves for 
additively manufactured Inconel 625. Metall. Mater. 
Trans. A 50, 457–467 (2019).
196.	Rai, A., Markl, M. & Körner, C. A coupled cellular 
automaton–lattice Boltzmann model for grain 
structure simulation during additive manufacturing. 
Comput. Mater. Sci. 124, 37–48 (2016).
197.	Zhang, Z. et al. Numerical methods for microstructural 
evolutions in laser additive manufacturing. Comput. 
Math. Appl. 78, 2296–2307 (2019).
198.	Wang, Y., Shi, J. & Liu, Y. Competitive grain growth 
and dendrite morphology evolution in selective laser 
melting of Inconel 718 superalloy. J. Cryst. Growth 
521, 15–29 (2019).
199.	Kumara, C. et al. Predicting the microstructural 
evolution of electron beam melting of alloy 718 with 
phase-​field modeling. Metall. Mater. Trans. A 50, 
2527–2537 (2019).
200.	Schänzel, M., Shakirov, D., Ilin, A. & Ploshikhin, V. 
Coupled thermo-​mechanical process simulation 
method for selective laser melting considering phase 
transformation steels. Comput. Math. Appl. 78, 
2230–2246 (2019).
201.	Denlinger, E. R., Gouge, M., Irwin, J. & Michaleris, P. 
Thermomechanical model development and in situ 
experimental validation of the laser powder-​bed  
fusion process. Addit. Manuf. 16, 73–80 (2017).
202.	Caggiano, A. et al. Machine learning-​based image 
processing for on-​line defect recognition in additive 
manufacturing. CIRP Ann. 68, 451–454 (2019).
203.	Chowdhury, S. & Anand, S. in ASME 2016 11th Int. 
Manuf. Sci. Eng. Conf. https://doi.org/10.1115/
MSEC2016-8784 (American Society of Mechanical 
Engineers Digital Collection, 2016).
204.	Dastjerdi, A. A., Movahhedy, M. R. & Akbari, J. 
Optimization of process parameters for reducing 
warpage in selected laser sintering of polymer parts. 
Addit. Manuf. 18, 285–294 (2017).
205.	Shevchik, S. A., Kenel, C., Leinenbach, C. &  
Wasmer, K. Acoustic emission for in situ quality 
monitoring in additive manufacturing using spectral 
convolutional neural networks. Addit. Manuf. 21, 
598–604 (2018).
206.	Shevchik, S. A., Masinelli, G. G., Kenel, C.,  
Leinenbach, C. & Wasmer, K. Deep learning for  
in situ and real-​time quality monitoring in additive 
manufacturing using acoustic emission. IEEE Trans. 
Industr. Inform. 15, 5194–5203 (2019).
207.	Wei, Q., Akrotirianakis, I., Dasgupta, A. & 
Chakraborty, A. Learn to learn: application to topology 
optimization. Smart Sust. Manuf. Syst. 2, 250–260 
(2018).
208.	Barrios, J. M. & Romero, P. E. Decision tree methods 
for predicting surface roughness in fused deposition 
modeling parts. Materials 12, 2574 (2019).
209.	Tootooni, M. S. et al. Classifying the dimensional 
variation in additive manufactured parts from laser-​
scanned three-​dimensional point cloud data using 
machine learning approaches. J. Manuf. Sci. Eng. 
139, 091005 (2017).
210.	He, H., Yang, Y. & Pan, Y. Machine learning for 
continuous liquid interface production: printing speed 
modelling. J. Manuf. Syst. 50, 236–246 (2019).
211.	 Gordon, E. R. et al. in Sustainable Design and 
Manufacturing 2016 (eds Setchi, R., Howlett, R. J.,  
Liu Y. & Theobald, P.) 423–434 (Springer International, 
2016).
212.	Gobert, C., Reutzel, E. W., Petrich, J., Nassar, A. R. & 
Phoha, S. Application of supervised machine learning 
for defect detection during metallic powder bed fusion 
additive manufacturing using high resolution imaging. 
Addit. Manuf. 21, 517–528 (2018).
213.	Song, L., Huang, W., Han, X. & Mazumder, J. Real-
time composition monitoring using support vector 
regression of laser-​induced plasma for laser additive 
manufacturing. IEEE Trans. Ind. Electron. 64, 633–642 
(2016).
214.	Zhang, J., Wang, P. & Gao, R. X. Deep learning-​based 
tensile strength prediction in fused deposition 
modeling. Comput. Ind. 107, 11–21 (2019).
215.	Chen, Z., Zong, X., Shi, J. & Zhang, X. Online 
monitoring based on temperature field features and 
prediction model for selective laser sintering process. 
Appl. Sci. 8, 2383 (2018).
216.	Aminzadeh, M. & Kurfess, T. R. Online quality 
inspection using Bayesian classification in powder-​bed 
additive manufacturing from high-​resolution visual 
camera images. J. Intell. Manuf. 30, 2505–2523 
(2019).
217.	Bacha, A., Sabry, A. H. & Benhra, J. Fault diagnosis  
in the field of additive manufacturing (3D printing) 
using Bayesian networks. Int. J. Online Eng. 15 
(2019).
218.	Li, J., Jin, R. & Hang, Z. Y. Integration of physically-​
based and data-​driven approaches for thermal field 
prediction in additive manufacturing. Mater. Des. 
139, 473–485 (2018).
219.	Tapia, G., Elwany, A. & Sang, H. Prediction of porosity 
in metal-​based additive manufacturing using spatial 
Gaussian process models. Addit. Manuf. 12, 282–290 
(2016).
220.	Aboutaleb, A. M. et al. Accelerated process optimization 
for laser-​based additive manufacturing by leveraging 
similar prior studies. IISE Trans. 49, 31–44 (2017).
221.	Tapia, G., Khairallah, S., Matthews, M., King, W. E.  
& Elwany, A. Gaussian process-​based surrogate 
modeling framework for process planning in laser 
powder-​bed fusion additive manufacturing of 316L 
stainless steel. Int. J. Adv. Manuf. Technol. 94,  
3591–3603 (2018).
222.	Martínez, J., Song, H., Dumas, J. & Lefebvre, S. 
Orthotropic k-​nearest foams for additive 
manufacturing. ACM Trans. Graph. 36, 121 (2017).
223.	Mutiargo, B., Garbout, A. & Malcolm, A. A. in 
International Forum on Medical Imaging in Asia 2019 
110500L (International Society for Optics and 
Photonics, 2019).
224.	Wu, M., Phoha, V. V., Moon, Y. B. & Belman, A. K.  
in ASME 2016 Int. Mech. Eng. Congress Exposition 
https://doi.org/10.1115/IMECE201667641 (American 
Society of Mechanical Engineers Digital Collection, 
2016).
225.	Qin, J., Liu, Y. & Grosvenor, R. A framework of energy 
consumption modelling for additive manufacturing 
using Internet of Things. Procedia CIRP 63, 307–312 
(2017).
226.	Alwoimi, B. M. Development of a Framework for 
Design for Additive Manufacturing (North Carolina 
A&T State University, 2018).
227.	Chou, R., Ghosh, A., Chou, S., Paliwal, M. & Brochu, M. 
Microstructure and mechanical properties of Al10SiMg 
fabricated by pulsed laser powder bed fusion.  
Mater. Sci. Eng. A 689, 53–62 (2017).
228.	Baturynska, I., Semeniuta, O. & Wang, K.  
in Advanced Manufacturing and Automation VIII. 
IWAMA 2018. Lecture Notes in Electrical Engineering 
Vol 484 (eds Wang, K., Wang, Y., Strandhagen, J. & 
Yu, T.) 245–252 (Springer, 2019).
229.	Paul, A. et al. A real-time iterative machine learning 
approach for temperature profile prediction in additive 
manufacturing processes in 2019 IEEE International 
Conference on Data Scienceand Advanced Analytics 
(DSAA) (eds, Singh, L., De Veaux, R., Karypis, G., 
Bonchi,F. & Hill, J.) 541–550 (IEEE, Piscataway, 2019).
230.	DeCost, B. L. & Holm, E. A. Characterizing powder 
materials using keypoint-​based computer vision 
methods. Comput. Mater. Sci. 126, 438–445 (2017).
231.	Mitchell, J. A. An Approach to Upscaling  
SPPARKS Generated Synthetic Microstructures of 
Additively Manufactured Metals (Sandia National 
Lab., 2019).
232.	Wang, Y., Lin, Y., Zhong, R. Y. & Xu, X. IoT-​enabled 
cloud-​based additive manufacturing platform to 
support rapid product development. Int. J. Prod. Res. 
57, 3975–3991 (2019).
233.	Koeppe, A., Padilla, C. A. H., Voshage, M., 
Schleifenbaum, J. H. & Markert, B. Efficient  
numerical modeling of 3D-​printed lattice-​cell 
structures using neural networks. Manuf. Lett. 15, 
147–150 (2018).
234.	Kunkel, M. H., Gebhardt, A., Mpofu, K. & Kallweit, S. 
Quality assurance in metal powder bed fusion via 
deep-​learning-based image classification. Rapid 
Prototyp. J. (2019).
235.	Francis, J. & Bian, L. Deep learning for  
distortion prediction in laser-​based additive 
manufacturing using big data. Manuf. Lett. 20, 
10–14 (2019).
236.	Mozaffar, M. et al. Data-​driven prediction of the  
high-​dimensional thermal history in directed energy 
deposition processes via recurrent neural networks. 
Manuf. Lett. 18, 35–39 (2018).
nature Reviews | MAteRiAlS
Reviews
	
 volume 6 | January 2021 | 67


237.	Gonzalez-​Val, C., Pallas, A., Panadeiro, V. &  
Rodriguez, A. A convolutional approach to quality 
monitoring for laser manufacturing. J. Intell. Manuf. 
31, 789–795 (2020).
238.	Petrich, J., Gobert, C., Phoha, S., Nassar, A. R.  
& Reutzel, E. W. in Proc. 27th Int. Solid Freeform 
Fabrication Symp. (eds Bourell, D. L., Crawford, R. H., 
Seepersad, C. C., Beaman, J. J. & Fish, S.)  
1660–1674 (The University of Texas, Austin, 2017).
239.	Murphy, C., Meisel, N., Simpson, T. & McComb, C.  
in Solid Freeform Fabrication 2018: Proc. 29th Annu. 
Int. Solid Freeform Fabrication Symp. — An Addit. 
Manuf. Conf. (eds Bourell, D. L, Beaman, J. J., 
Crawford, R. H., Fish, S. & Seepersad, C., C.)  
1363–1381 (The University of Texas, Austin, 2018).
240.	Lu, X. et al. Open-​source wire and arc additive 
manufacturing system: formability, microstructures, 
and mechanical properties. Int. J. Adv. Manuf. Technol. 
93, 2145–2154 (2017).
241.	Gong, X. & Chou, K. Phase-​field modeling of 
microstructure evolution in electron beam additive 
manufacturing. JOM 67, 1176–1182 (2015).
242.	Tan, J. L., Tang, C. & Wong, C. H. A computational 
study on porosity evolution in parts produced by 
selective laser melting. Metall. Mater. Trans. A 49, 
3663–3673 (2018).
Author contributions
All authors contributed in researching previous works, discus-
sions of the contents of the manuscript, writing portions of 
the text and reviewing and editing the manuscript.
Competing Interests
The authors declare no competing interests.
Publisher’s note
Springer Nature remains neutral with regard to juris­dictional 
claims in published maps and institutional affiliations.
 
© Springer Nature Limited 2020
www.nature.com/natrevmats
Reviews
68 | January 2021 | volume 6	



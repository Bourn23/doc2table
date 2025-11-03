Available online at www.sciencedirect.com
ScienceDirect
Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
www.elsevier.com/locate/cma
Eigenvector sensitivity when tracking modes with repeated
eigenvalues
D. Ruiz, J.C. Bellido∗, A. Donoso
Departamento de Matemáticas, ETSII Universidad de Castilla-La Mancha, 13071 Ciudad Real, Spain
Received 24 March 2017; received in revised form 2 June 2017; accepted 26 July 2017
Available online 12 August 2017
Abstract
While eigenvalue optimization problems have been widely studied during the last three decades, particularly for structural
and topology optimization problems, there are very few examples of problems involving mode shapes either in the cost or the
constraints. In this paper, we propose a general framework for computing eigenvector sensitivity whenever tracking specific mode
shapes selected beforehand. Of course, the approach is valid for either non-repeated or repeated eigenvalues, but here the emphasis
is placed on the multiple eigenvalues case. Both mathematical validity of the algorithm and numerical corroboration through several
examples are included.
c⃝2017 Elsevier B.V. All rights reserved.
Keywords: Eigenvector derivative; Repeated eigenvalues; Mode shape derivative; Eigenmode optimization; Eigenmode selection; Modal
assurance criterion
1. Introduction
Eigenvalue optimization problems appear very frequently when dealing with structural stability and vibration
analysis, and nowadays it is a very well understood topic in topology optimization [1]. Eigenvalue sensitivity analysis
for this kind of problems is a classic issue dating back to the sixties. For eigenvalue sensitivity calculation there are
two different cases: simple, non-repeated, or multiple, repeated, eigenvalues, being this last case much more difficult
and subtle than the former one, since multiple eigenvalues are not differentiable. There are many references where
this has been addressed, and among those we cite [2,3]. Sensitivity analysis has been applied for optimization of
eigenvalues for free vibrations together with proper model formulations like the bound formulation (see [1,4] and the
references therein).
Optimization problems involving eigenmodes, i.e. such that either cost or constraints depends on eigenmodes are
much more scarce in the literature. However, in the last years several models requiring to optimize eigenmodes or
constraining functionals depending on eigenmodes have been studied. In [5], a mode shape corresponding to a simple
∗Corresponding author.
E-mail address: JoseCarlos.Bellido@uclm.es (J.C. Bellido).
http://dx.doi.org/10.1016/j.cma.2017.07.031
0045-7825/ c⃝2017 Elsevier B.V. All rights reserved.


D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
339
eigenvalue of a fiber laser package is designed in order to minimize the elongation of the fiber under dynamic excita-
tion. In [6], a multi-objective function is formulated in order to find optimal configurations that simultaneously satisfy
(simple) eigenfrequency, eigenmode, and stiffness requirements at certain points of a vibrating structure. A similar
problem is treated in [7]. The novelty there is to include the electromechanical coupling coefficient in the objective
function so that the energy conversion is maximized for a specific mode. In [8], eigenmodes appear in the constraints
only. One of the objectives of that work is to determine the material distribution of a structure that maximizes the fun-
damental frequency and at the same time synthesizes the first two modes. Recently, in [9] an optimization problem in
which both cost and constraints depend on eigenmodes has been studied, and furthermore, all the pathologies appear-
ing when dealing with eigenproblems are present: spurious modes, mode switching and multiple eigenfrequencies.
The objective in that paper is the optimal design of piezoelectric modal sensor/actuators, in which we simultaneously
designed the ground structure and polarization profiles of the piezoelectric transducers (see the recent survey [10]).
One of the main difficulties when dealing with eigenmode optimization is the sensitivity analysis. Eigenvector
sensitivity for structural analysis problems has been addressed in [11–19]. The first issue is about differentiability,
while eigenmodes corresponding to non-repeated eigenvalues are differentiable, eigenmodes corresponding to
repeated ones are not even continuous. This is due to the fact that there are infinite eigenvector basis of the eigenspace
associated to a multiple eigenvalue, so that this ambiguity spoils continuity and therefore differentiability. However,
differentiability can be guaranteed for a concrete eigenvector basis, the so-called adjacent basis, and for it explicit
derivative computations can be performed. Further to this, the eigenvector derivative computation leads to solve
degenerate linear systems for which specific methods have been developed [11,13,14,16,17].
Another crucial point is eigenmode selection. When a functional involved in the optimization problem, either the
cost or a constraint, depends on a mode shape it must be very clear on which specific mode shape is such a dependence,
since mode shapes change and mode switching (change of order of eigenvalues in the spectrum) happens during the
optimization process when updating variables. Therefore cost and constraints must clearly depend on selected mode
shapes. In [9], a procedure for selecting the closest mode shapes to given reference mode shapes was developed. This
procedure follows the idea and spirit of the well-known modal assurance criterion [20] but including the possibility
of repeated eigenvalues appearance. The difficulty now is that once eigenmodes have been selected, the optimization
algorithm requires derivatives for those specific eigenmodes. This is not an issue for eigenmodes associated with
non-repeated eigenvalues since those are differentiable, but if they are associated with repeated ones, then available
methods only provide derivatives for the adjacent basis of eigenvectors. For the specific situation considered by
the authors in [9], a heuristic method working out for obtaining these derivatives was developed. The aim of this
paper is to deepen those ideas whenever tracking specific mode shapes with three objectives in mind: establish a
method of eigenmode selection suitable for a wide range of situations of eigenmode optimization models, give a
general algorithm for computing derivatives of selected eigenmodes valid for the case of repeated and non-repeated
eigenvalues, and finally, analyze the mathematical foundations of the algorithm in order to show its validity. These
three objectives have been reached in this paper.
The paper is organized as follows. In Section 2 we review the main algorithms for eigenvector derivatives
computation and comment on differentiability, clarifying some misleading ideas and claims present in the literature. In
Section 3 we present a method for eigenmode selection and for the calculation of derivatives of selected eigenmodes.
The algorithm validity is numerically corroborated with two structural analysis examples. Finally, in Section 4 we
consider an example of an eigenmode optimization problem inspired by [9] in order to numerically validate the
previous algorithm in a real optimization problem.
2. Review of current methods for eigenvectors sensitivity analysis
Given K, M ∈Rn×n real, symmetric and positive definite matrices. We are interested in the eigenproblem
(K −λM)U = 0.
(1)
In structural dynamics, K stands for the stiffness matrix, M the mass matrix, λ the eigenvalues or eigenfrequencies,
i.e. the square of the natural frequencies, and U stands for the mode shape, or eigenvector, corresponding to the
eigenfrequency λ.
It is well known that under these conditions all the eigenfrequencies are real, λ1 ≤· · · ≤λn ∈R, and there exists
a M-orthonormal basis of Rn made of eigenvectors U1, . . . , Un, i.e.
(K −λ jM)U j = 0
(2)


340
D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
and
UT
i MU j = δi j,
i, j = 1, . . . , n,
(3)
where δi j is the Kronecker’s delta.
We assume that both mass and stiffness matrices depend smoothly on a vector of real variables x = (x1, . . . , xL) ∈
RL, that usually represents a physical magnitude for the different elements of a finite element mesh, as Young’s
modulus, Poisson’s ratio, thickness, moment of inertia, etc. We are interested in the computation of the eigenproblem
sensitivity with respect to x. In particular, our main interest is the eigenvectors sensitivity.
Let us begin by doing some formal computations for obtaining the derivatives with respect to the single variable
xi, the ith component of x. Differentiating (2) with respect to xi,
∂
∂xi
(
(K −λ jM)U j
)
= 0,
(4)
and operating we arrive at
(
K −λ jM
) ∂U j
∂xi
= −
(∂K
∂xi
−λ j
∂M
∂xi
)
U j + ∂λ j
∂xi
MU j.
(5)
Therefore, the derivative of the eigenvector with respect to the variable,
∂U j
∂xi , if it exists, is the solution of a degenerate
system (det
(
K −λ jM
)
= 0). Furthermore, the right hand side of (5) depends on the eigenfrequency derivative, so
that it must exist for the eigenvector derivative to exist. At this point, to go further in this computation we should
distinguish between two cases depending on whether the eigenfrequency λ j is simple or multiple, i.e. λ j a non-
repeated or repeated eigenvalue.
2.1. Simple eigenfrequencies
In the case that λ j is a simple eigenvalue for (2), eigenvectors associated to it are unique up to a multiplicative
constant. In this case, it is well known that both eigenvalues and eigenvectors are differentiable with respect to x,
provided matrices K and M so are with respect to x. See, for instance, [2] or [21] where a nice analytic proof of this
fact based on the Implicit Function Theorem is given.
From now on ( )′ stands for the derivative with respect to the parameter xi. For obtaining the derivatives we
premultiply both sides of Eq. (5) by UT
j and, taking into account (2) and (3), the expression for the partial derivative
of λ j with respect to xi is
λ′
j = UT
j
(
K′ −λ jM′)
U j.
(6)
Notice that the computation of the sensitivity of the jth eigenvalue only requires the jth eigenvector. This is an
important fact regarding other methods based on spectral or singular values expansions requiring all the eigenvectors
in order to compute any eigenvalue derivative [12,19]. Indeed, this is also an important advantage when working
in structural problems where the size of the matrices K and M is typically large and then the computation of all
eigenvalues and eigenvectors would be computationally prohibitive.
Regarding the computation of the eigenvector derivative, as we mentioned above, we have to solve system (5),
and the matter is that this is a degenerate system as the coefficients matrix has rank n −1. There are several ways
to overcome this difficulty, being the most popular one the Nelson’s method [16]. The idea is to replace a redundant
equation in (5) with Eq. (3), or more properly, the derivative of this identity,
UT
j MU′
j = −1
2UT
j M′U j.
(7)
To this end, the eigenvector derivative with respect to xi is decomposed as the sum of a particular solution, called V j
and the homogeneous solution, c jU j, with c j a constant to be determined,
U′
j = V j + c jU j.
(8)
A summary of the process is shown in Table 1.


D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
341
Table 1
The procedure of Nelson’s method.
1. Compute the eigenvalues derivatives λ′
j = UT
j (K′ −λ jM′)U j.
2. Set G j ≡K −λ jM and f j ≡λ′
jMU j −(K′ −λ jM′)U j.
3. Identify the largest element in U j, placed in the kth position.
4. Construct G j by zeroing out the kth row and the kth column in
G j and setting the diagonal element equal to 1.
5. Construct f j by zeroing out the kth element of f j.
6. Compute V j by solving the system f j = G jV j.
7. Set c j = −VT
j MU j −0.5UT
j M′U j. c j is obtained from (7).
8. Finally U′
j = V j + c jU j.
Fig. 1. Evolution of eigenvalues with the variable.
Again, a remarkable fact on Nelson’s Method is that computations of the partial derivatives of the jth eigenvalue
and the jth eigenvector only depend on the own jth eigenpair itself. Other related methods use a linear combination
of eigenvectors, ∑n
j=1c jU j, as the homogeneous solution of (5).
When we are dealing with optimization problems depending on modes, we typically have to compute derivatives of
linear functions of the eigenmodes rather than eigenmodes derivatives themselves. In [22], a procedure for computing
derivatives with respect to all the variables at once for this kind of functionals was developed. It is valid for the case
of eigenvectors corresponding to simple eigenvalues only, but this is still very remarkable from a computational point
of view.
2.2. Multiple eigenfrequencies
The typical situation, but not the only one, in which multiple eigenvalues appear is that two different eigenvalues
coalesce at a certain value of the variables vector x, and split out under a small perturbation on any xi. For instance,
for a double eigenvalue (also the most common situation when repeated eigenvalues occur) this can be understood
in terms of non-smooth analysis [23]. The subderivative with respect to a single, real variable, is defined as the set
of slopes of any tangent straight line to the graph of the eigenvalue, and so in this situation the subderivative is a
closed interval whose extreme points are the derivatives of the two coalescent eigenvalues (see Fig. 1). There are
well established techniques both for computing multiple eigenvalues derivatives and for dealing with eigenvalues
optimization problems (see [1] and the references therein).
For a multiple eigenvalue, λ j, there are infinitely many M-orthonormal basis of eigenvectors associated to λ j. This
fact makes eigenvectors differentiability, and even continuity, to fail. To understand this issue we include, for the
interest of the reader, a very simple and clarifying example taken from [18].
Let us consider the eigenvalue problem
[1
x
x
1
]
U = λU,
(9)


342
D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
where x ∈R is the single variable. Clearly, eigenvalues are 1 −x and 1 + x, and an orthonormal basis of eigenvectors
written in matrix form is
[−1
1
1
1
]
.
(10)
For x = 0, simple eigenvalues coalesce at a double one, and any basis in R2 is an eigenvectors basis, spoiling
continuity. However, the previous basis would be valid as eigenvector basis when x = 0, and for it, continuity
would be preserved. This is the idea in computing eigenvector derivatives, that there exists a M-orthonormal basis of
eigenvectors which is differentiable with respect to single variables. This basis is sometimes called in the literature
adjacent basis, keeping in mind the idea that eigenvalues split out when a perturbation is applied to the variable, and
then being both eigenvalues and eigenvectors differentiable.
Let λ be an eigenvalue of multiplicity m. For computing the right basis of eigenvectors we proceed in the following
way. Let us consider an initial matrix U whose columns, U1, . . . , Um, are M-orthonormal eigenvectors associated to
λ, i.e.
KU = MUΛ,
(11)
and
UT MU = Im,
(12)
where Λ = λIm, and Im is the identity matrix of order m. Any other set of m M-orthonormal vectors can be obtained
from U through an orthogonal transformation
Z = UΓ,
(13)
with Γ an orthogonal matrix (i.e. ΓT Γ = I). Imposing the eigenproblem to Z we get,
KZ = MZΛ,
(14)
and differentiating and arranging terms we arrive at
(K −λM) Z′ = −
(
K′ −λM′)
Z + MZΛ′.
(15)
Λ′ is the m × m diagonal matrix whose diagonal elements are the m derivatives of λ [3]. Multiplying now by UT and
taking into account (11)–(13) we get that Γ and Λ′ are the solutions of the eigenproblem
DΓ = ΓΛ′,
(16)
where D is the m × m matrix
D = UT (
K′ −λM′)
U.
(17)
D is symmetric and therefore Γ is orthogonal.
For solving system (15), Nelson’s method is not operative since it is based on the fact that rank(K −λM) = n −1,
that is not true for multiple eigenvalues. Several modifications of Nelson’s method have been introduced to overcome
this difficulty. The most extended extension of Nelson’s method to multiple eigenvalues is the Dailey’s method [11]
(that improved the previous Ojalvo’s method [17]). This method is valid for the case in which eigenvalues derivatives
are different, being the most usual situation when dealing with structural or topology optimization problems where,
on the one hand, due to symmetry one may have multiple eigenfrequencies in the initial layout that separate when
variables are updated, or on the other hand, two eigenvalues coalesce at a certain iteration of the algorithm. In Table 2
the summary of the algorithm for an eigenvalue of multiplicity m is presented. For technical details and the justification
of the algorithm readers are referred to [11].
Notice that the main idea is, as in Nelson’s method, to write eigenvectors derivatives as the sum of a solution of a
linear transformation of the eigenvectors (solution of the homogeneous system) and a particular solution of (15).
Obviously, construction of matrix C (Table 2) in the Dailey’s algorithm is not compatible with equal eigenvalues
derivatives. As we mentioned above, this is an uncommon situation in structural optimization, but of course it may
happen sometimes. In [13], this situation was analyzed, and academic examples were included, as for instance, a
circular shaft symmetric in both axes and such that variables are chosen so that symmetry is retained. Friswell solved


D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
343
Table 2
The procedure of Dailey’s method.
1. Given an initial set of M-orthonormal m eigenvectors of λ arranged in a matrix U, compute, as explained above, the adjacent eigenvectors:
Z = UΓ.
2. Set G ≡K −λM and f ≡Λ′MZ −(K′ −λM′)Z.
3. Identify the m largest elements in matrix Z, placed in the k1th, . . . , kmth positions.
4. Construct G by zeroing out the klth rows and the klth columns, l = 1, . . . , m, in G and setting the diagonal elements equal to 1.
5. Construct f by zeroing out the klth elements of f, l = 1, . . . , m.
6. Compute V by solving the system f = GV.
7. Compute Q = −VT MZ −ZT MV −ZT M′Z.
8. Compute R = ZT (K′ −λM′)V −ZT (M′Z + MV)Λ′ + 0.5ZT (K′′ −λM′′)Z.
9. Let C be the m × m matrix given by:
cik =
{rik/(λ′
k −λ′
i)
if
λ′
k ̸= λ′
i
0.5qik
otherwise
(18)
10. Finally, Z′ = V + ZC.
Table 3
The procedure of Friswell’s method.
1. Compute the matrix D = UT (K′ −µM′)U.
2. Solve the eigenproblem DΓ = ΓΛ′. Note than in this case matrix Γ is not unique, since the eigenvalues of D are repeated.
3. Compute the adjacent eigenvectors, Z = UΓ
4. Set G ≡K −λM and f ≡Λ′MZ −(K′ −λM′)Z.
5. Identify the m largest elements in matrix Z, placed in the k1th, . . . , kmth positions.
6. Construct G by zeroing out the klth row and the klth column, l = 1, . . . , m, in G and setting the diagonal elements equal to 1.
7. Construct f by zeroing out the klth elements of f, l = 1, . . . , m.
8. Compute V by solving the system f = GV.
9. Compute VΦ = VΓ.
10. Compute ΓΦ by solving the next eigenproblem: 2UT (K′ −λM′ −λ′M)VΦΓΦ + UT (K′′ −λM′′ −2λ′M′)UΓΦ = Λ′′ΓΦ. Λ′′
stands for the second eigenvalues derivatives.
11. Since the eigenvalues of the previous eigenproblem are single, ΓΦ is unique. If Γ ̸= ΓΦ, set Γ = ΓΦ and Z = UΓ.
12. Set H ≡K −λM and Ji ≡−2(K′ −λM′ −λ′M)(Vi + ZCi) −(K′′ −λM′′ −λ′′
i M −2λ′M′)Zi.
13. Identify the m largest elements in matrix Z, placed in the klth positions, l = 1, . . . , m.
14. Construct H by zeroing out the klth row and the klth column, l = 1, . . . , m, in H and setting the diagonal elements equal to 1.
15. Construct J by zeroing out the klth element of J, l = 1, . . . , m.
16. Compute Wi by solving the system Ji = HWi.
17. Compute the off-diagonal elements of matrix C by solving the next equation: 3ZT
j (K′ −λM′ −λ′M)Wi + 3ZT
j (K′′ −λM′′ −λ′′
i M
−2λ′M′)(Vi + ZCi) + ZT
j (K′′′ −λM′′′ −3λ′M′′ −3λ′′
i M′)Zi = 0, for j ̸= i.
18. Compute the elements of the diagonal of matrix C as: Cii = −0.5ZT
i M′Zi −VT
i MZi.
19. Finally, the sensitivity of the eigenvectors is Z′ = V + ZC.
this situation giving an efficient method for eigenvector derivative calculation in this situation. Table 3 summarizes
this algorithm. Notice that in this situation matrix Γ for the computation of the adjacent eigenvectors is not unique,
since there are equal eigenvalue derivatives in this case, so that a method has to be included in order to find the right
set of adjacent eigenvectors for which derivatives can be calculated. For the technical details justifying this method
we refer readers to [13].
Nelson, Dailey and Friswell’s are the three essential algorithms for computing eigenvector derivatives. There are
however interesting refinements or modifications that could be of interest in certain situations, and, without doubt,
worth mentioning. A key point in these algorithms is the solution of the degenerate linear system GV = f (indeed
in Friswell’s method this kind of calculation has to be performed twice), that it is solved by zeroing out certain rows
and columns of the system matrix. With this procedure one gets a linear system admitting a unique solution, but its
matrix might be poorly conditioned. To circumvent this issue, in [15] an iterative algorithm for solving this system is
proposed, including an analysis of convergence of the method. In [14] an interesting method for computing solutions
to this system is proposed by adding m (recall that m is the eigenvalue multiplicity) new equations to it. Their method


344
D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
also works out when equal eigenvalue derivatives of any order of derivation occur, what is not considered by the
Friswell’s method.
2.3. Remarks on differentiability
The previous methods provide the derivatives of eigenvalues and eigenvectors assuming those to exist. Since
literature is somehow confusing regarding whether eigenvalues and eigenvectors are differentiable or not, in the sense
that there are misleading comments or claims in several references, specially in those pertaining to the mechanical
engineering literature, we would like, to the best of the authors knowledge, to clarify this issue by indicating proper
references and known results.
The first point to take into account is that beyond eigenvalues and eigenvectors derivatives with respect to a single
real variable, in practical optimization problems more than this is required, we actually need to have differentiability
with respect to a vector of variables, meaning that jacobian matrix can be computed (all partial derivatives exist) and
any directional derivative coincides with the jacobian matrix acting on the direction.
When an eigenvalue is simple, and stiffness and mass matrices, K and M, are continuously differentiable with
respect to a single real variable, then differentiability of both eigenvalue and associated eigenvectors holds. There are
several references where this is shown, and we have already cited [2,21], and now we add [24]. When the eigenproblem
depends on a vector of variables, with K and M continuously differentiable with respect to this vector, since partial
derivatives with respect to each single variable are continuous, then differentiability with respect to the variables
vector of both the single eigenvalue and its associated eigenvectors holds as well.
The situation for multiple eigenvalues is much more difficult. When considering eigenvalue differentiability with
respect to a single variable, [24, Th. 6.8] establishes that if matrices K and M are continuously differentiable then
there exist n continuously differentiable functions that represent the (repeated) eigenvalues of the eigenproblem.
Differentiability is broken when eigenvalues coalesce if we name then by the usual increasing order, as Fig. 1
graphically shows. Regarding eigenvector differentiability with respect to a single variable when multiple eigenvalue
happens, the situation is more subtle. On the one hand, additional smoothness of the eigenproblem with respect to
the variable is required. [24, Ex. 5.3] gives an example in which matrices K and M are not analytical with respect
to variables and continuity of eigenvectors fails at the point where eigenvalues coalesce, so that analyticity of the
eigenproblem with respect to the variable is the minimal hypothesis in order to guarantee eigenvectors differentiability.
This is not an issue for structural, or topology, optimization problems where stiffness and mass matrices dependence
of variables is usually polynomial, and therefore analytic. Under this analyticity hypothesis, it is shown in
[24, Section 6.2], that there exists a M-orthonormal basis of Rn of eigenvectors continuously differentiable (and
in fact analytic) with respect to the variable. This is congruent with the previous methods for computing eigenvectors
derivatives, where the first step consists in finding the adjacent eigenvectors, which are the eigenvectors that the
multiple eigenvalue contributes to the continuously differentiable M-orthonormal basis of eigenvectors.
Concerning differentiability with respect to a vector of variables, multiple eigenvalues are not differentiable (in
the Fr´echet sense) with respect to the full vector of variables, but they are Gˆateaux differentiable, i.e. directional
derivatives do exist at any direction. Proofs of this fact and formulas for the directional derivatives can be found
in [2]. Regarding eigenvectors, the continuously differentiable M-orthonormal basis of eigenvectors mentioned in the
previous paragraph depends in general on the single variable (in the notation of the previous subsection, the matrix Γ
depends on the variable with respect to which we are computing derivatives), so that, in general, there does not exist
an M-orthonormal basis of eigenvectors differentiable with respect to the variables vector [24]. Ref. [13] reports about
this issue, including examples in which the basis keeps constant for all the variables, and therefore differentiability is
granted. However, for a fixed mode shape one could compute partial derivatives as linear combination of derivatives
of the differentiable basis with respect to single variables, and finally to write the jacobian matrix of the fixed mode
shape concluding its differentiability since partial derivatives are continuous.
Optimization problems in which cost or constraints depend on eigenvectors usually select them through a criterion
permitting to follow a certain desired given mode shape. For instance, a problem in which we would like to find the
structure optimizing a cost depending on the structure mode shape closed to a given reference one. Thinking in plate-
type structures, that could be a prescribed mode shape of the whole plate (i.e., the whole domain) while optimizing
the structure inside the domain. Of course, we would need derivatives for such eigenvectors, that eventually will
correspond to double (or in general multiple) eigenvalues. Next section is devoted to this issue.


D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
345
3. Practical computation of derivatives for selected eigenmodes
In the previous section, classical methods for the computation of derivatives with respect to single variables
of eigenvectors associated to multiple eigenvalues have been introduced and commented. Those methods only
provide derivatives of a certain eigenvector basis, the so-called adjacent eigenvector basis, associated to the multiple
eigenvalues. On the other hand, when we have an optimization problem in which cost, constraints, or both, depend
on eigenvectors, gradient-based optimization algorithms require the computation of the eigenvector derivatives, and
those eigenvectors may not belong to the adjacent eigenvector basis in the case of repeated eigenfrequencies. In
this section we go a step further of this by computing derivatives for fixed, or selected, eigenmodes associated to
the multiple eigenvalues but not being an adjacent eigenvector in general. For this situation we propose a procedure
that will be corroborated numerically with several examples. Our method provides the derivatives of any selected
eigenvector taking advantage of the fact that any eigenvector associated to a multiple eigenvalue can be obtained as
a linear expansion of the adjacent eigenvectors of such an eigenvalue. Our procedure admits multiple selection of
eigenmodes, actually for the whole eigenvector basis. Our method is not an alternative to the previous methods, but a
procedure for their practical implementation in optimization problems.
There are two issues to be solved. First, the derivative computation itself, and second the selection of the
eigenmodes. The first one is easily solved. For computing the derivative of a fixed eigenmode we take advantage of
the linear structure of the set of eigenmodes associated to a multiple eigenvalue. Let λ be an eigenvalue of multiplicity
m, and v an eigenmode associated to λ, i.e. (K −λM)V = 0, then the derivative of V is computed in the following
way:
1. Find the adjacent basis of eigenvectors,
Z(1), . . . , Z(m);
2. Compute the derivative of this vectors by any of the previous methods, Dailey’s method if possible, for instance;
3. Write the selected eigenmode as a linear expansion of the adjacent eigenvectors,
V = c1Z(1) + · · · + cmZ(m),
or in matrix form
V = ZC,
where Z is the matrix of columns Z(1), . . . , Z(m) and C = (c1, . . . , cm)T ;
4. The derivative of the fixed mode is the linear expansion of the derivative of the adjacent eigenmodes with the
same coefficients,
V′ = c1
(
Z(1))′ + · · · + cm
(
Z(m))′ = Z′C.
We would like to emphasize that, to the best of the authors knowledge, this algorithm, in spite of it is natural and
easy, has not been neither proposed nor used in the literature before.
Regarding the second issue, the eigenvectors selection can be explicitly given by the model, but in general reference
eigenvectors must be computed by solving an optimization problem in order to fulfill a proximity criterion in the spirit
of the Modal Assurance Criterion (see [20] and the references therein). The idea is to select the closest eigenmodes
to given vectors (which typically are eigenmodes of the structure filling the whole design domain). Therefore, if ˜Y
is the matrix containing these target vectors (in the same number than the multiplicity of the eigenvalue, this is not
strictly necessary but convenient as we point out below), U is an initial eigenvector basis associated to the repeated
eigenvalue (given by any numerical algorithm we may use), then the reference (or selected) eigenvectors, i.e. those
taking part in our optimization algorithm, are obtained as
Y = UΓ0,
(19)
where the orthogonal matrix Γ0 is the unique solution of
⎧
⎨
⎩
max
Γ0 : Γ0ΓT
0 =I
:
∥˜YT MY∥
s.t. :
Y = UΓ0.
(20)


346
D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
Table 4
Derivative of a selected eigenmode.
1. Compute the reference set of eigenvectors, Y, through the optimization problem (20).
2. Compute the matrix D as: D = YT (K′ −λM′)Y, and solve the eigenproblem (16).
3. Adjacent eigenvectors are Z = YΓ, with Γ given by (16).
4. Compute Z′ by using Dailey’s (or Friswell’s, if necessary) method.
5. Compute the derivatives as Y′ = Z′Γ−1 = Z′ΓT .
We select as many eigenvectors as the multiplicity of the eigenvalue, this is not strictly necessary but convenient
taking into account that for computing the derivative of an eigenvector associated to a multiple eigenvalue we need to
know both an adjacent basis of eigenvectors and their derivatives. This multiple selection procedure, even in the spirit
of MAC, seems also to be a novelty of this paper, as far as the authors may claim.
Once the reference eigenvectors are computed, the adjacent eigenvectors are calculated from them, and derivatives
are obtained from the derivatives computed for the adjacent eigenvectors using the linear transformation from this
former basis to the reference one. This is summarized in Table 4.
The validity of this procedure is shown through two examples. First, a square plate clamped at its four edges with
four elements and degrees of freedom, and second, a two-element cantilever. In both of them, we compute eigenvector
derivatives using our method and by numerical differentiation, checking that the same numerical results are obtained.
We would like to remark that those examples are to a certain extend artificial since those have been built up to illustrate
our method.
Four-edge clamped plate
In this example a square plate, shown in Fig. 2, is considered in order to ensure repeated natural frequencies. Four
square finite elements are used to model the plate. The elemental stiffness and mass matrices are defined as
Ke =
E0t
8(1 −ν2)
⎡
⎢⎢⎢⎢⎢⎢⎢⎢⎢⎢⎣
4
1
−2
−1
−2
−1
0
1
1
4
1
0
−1
−2
−1
−2
−2
1
4
−1
0
−1
−2
1
−3
0
−1
4
1
−2
1
−2
−2
−1
0
1
4
1
−2
−1
−1
−2
−1
−2
1
4
1
0
0
−1
−2
1
−2
1
4
−1
1
−2
1
−2
−1
0
−1
4
⎤
⎥⎥⎥⎥⎥⎥⎥⎥⎥⎥⎦
+
E0tν
24(1 −ν2)
⎡
⎢⎢⎢⎢⎢⎢⎢⎢⎢⎢⎣
4
3
−2
9
2
−3
4
−9
3
−4
−9
4
−3
2
9
−2
−2
−9
−4
−3
4
9
2
3
3
4
−3
−4
−9
−2
3
2
2
−3
4
−9
−4
3
−2
9
−3
2
9
−2
3
−4
−9
4
4
9
2
3
−2
−9
−4
−3
−9
−2
3
2
9
4
−3
−4
⎤
⎥⎥⎥⎥⎥⎥⎥⎥⎥⎥⎦
,
(21)
where E0 is the Young’s modulus of the material, t is the thickness and ν is the Poisson’s ratio.
Me = ρmtL2
36
⎡
⎢⎢⎢⎢⎢⎢⎢⎢⎢⎢⎣
4
0
2
0
1
0
2
0
0
4
0
2
0
1
0
2
2
0
4
0
2
0
1
0
0
2
0
4
0
2
0
1
1
0
2
0
4
0
2
0
0
1
0
2
0
4
0
2
2
0
1
0
2
0
4
0
0
2
0
1
0
2
0
4
⎤
⎥⎥⎥⎥⎥⎥⎥⎥⎥⎥⎦
,
(22)
being ρm the material density and L the element length.


D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
347
Fig. 2. Four-edge clamped plate.
This structural problem involves one variable ρe per element, which is the structural density of the finite element.
ρe = 0 and ρe = 1 mean void and solid, respectively [1].
Global stiffness and mass matrices (both depending linearly with the structural variable ρe) are constructed by
assembling the element matrices Ke and Me in the usual way,
K =
4
∑
e=1
ρeKe,
M =
4
∑
e=1
ρeMe.
(23)
The eigenproblem is expressed as follows,
{(K −λ jM)U j = 0,
j = 1, 2
UT
i MU j = δi j,
i, j = 1, 2 ,
(24)
where the vector U stores the displacements of the free node in the x- and y-axes,
U =
[ux
uy
]
.
(25)
Set E0 = 1, ν = 0.3, L
= 0.5, t
= 0.01, ρm
= 1. We compute derivatives when variables vector
x = ρ = [ρ1, ρ2, ρ3, ρ4] = [1, 1, 1, 1]. For these values of ρ, eigenvalues are double and equal to 17.8022,
and obtained eigenvectors (by a standard algorithm for computing eigenvectors) are collected into the matrix U,
U =
[21.2159
21.2159
21.2159
−21.2159
]
.
(26)
The target vectors are obtained from those eigenvectors under the action of a rotation, getting the ones parallel to the
x- and y-axes, that is,
˜Y =
[30.0000
0.0000
0.0000
30.0000
]
.
(27)
The eigenvectors U and ˜Y are represented in Fig. 3 (both sets are scaled, since the M-normalized displacements are
large).
In general, the reference set of eigenvectors Y should be obtained from ˜Y through the procedure of the previous
section, i.e. through the optimization problem (20), that is to say
Y = ˜UΓ0,
with Γ0 the optimal solution of
⎧
⎨
⎩
max
Γ0 : Γ0ΓT
0 =I
:
∥˜YT MY∥
s.t. :
Y = UΓ0.
Eventually, it could happen Y = ˜Y if the columns of ˜Y are an M-orthonormal eigenvectors basis of the same
eigenvalue, which is the case of this example since ˜Y is obtained from U under the action of a rotation, so that
Y = ˜Y.
Thanks to the symmetry of the problem, the derivatives with respect to any of the four variables are very similar,
so that for the sake of brevity only the derivatives with respect to ρ1 will be shown. The procedure is the following:


348
D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
Fig. 3. Set of obtained eigenvectors U (left) and reference eigenvectors ˜Y (right).
1. Compute the adjacent eigenvectors from Y, i.e. solve the eigenvalue problem
DΓ = ΓΛ′,
with
D = YT (K′ −λM′)Y,
and the adjacent eigenvectors are obtained as
Z = YΓ.
Notice that Λ′ is a diagonal matrix whose diagonal elements are the eigenvalue derivatives, which in this case
are different permitting to use Dailey’s method. Solving (16) we arrive at
Γ =
[0.7071
0.7071
0.7071
−0.7071
]
and
Λ′ =
[4.0797
0
0
13.7225
]
.
Now, we can compute the adjacent eigenvectors
Z =
[21.2132
21.2132
21.2132
−21.2132
]
.
2. Compute the adjacent eigenvectors derivatives by Dailey’s method. We obtain
∂Z
∂ρ1
=
[−2.6517
−2.6517
−2.6517
2.6517
]
.
3. Compute the derivative of Y as
∂Y
∂ρ1
= ∂Z
∂ρ1
ΓT ,
obtaining
∂Y
∂ρ1
=
[−3.7500
0.0000
0.0000
−3.7500
]
.
Now, in order to validate our procedure, we compute these derivatives by numerical differentiation and check
that the results coincide with those obtained with our analytical method. The numerical derivatives of the problem


D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
349
are computed by using finite-difference methods. Both eigenvalues, λ1, λ2, are different and coalesce at the point
ρ = [1, 1, 1, 1]. After this point, the eigenvalues separate again, but their order has changed, as shown in Fig. 1.
Backward formula is used instead of the centered one in order to prevent errors due to this fact. We remark that a
centered scheme could be used but taking into account the eigenvalues change off. The first order backward formula
used to compute numerically the derivatives with respect to ρ1 is expressed as follows:
∂NY
∂ρ1
=
Yρ1 −Yρ−
1
hN
,
where hN is the step, ∂NY/∂ρ1 is the numerically computed derivative and Yρ−
1 are the set of eigenvectors obtained
by solving Eq. (24) when the structural density of the first discrete element is perturbed as follows: ρ−
1 = ρ1 −hN.
Taking step hN = 10−3 the numerical derivatives are
∂NY
∂ρ1
=
[−3.7507
0.0000
0.0000
−3.7507
]
.
(28)
In this example the analytically and numerically computed derivatives differ no more that 0.02%, showing and
corroborating the validity of our method.
Two-element cantilever
In this example we consider a beam-type finite element model for the cantilever shown in Fig. 4. For the sake
of clarity only two finite elements are used, with 8 degrees of freedom per element, as usual for beam-type finite
elements.
The element stiffness and mass matrices are given by the following expressions:
Ke = E0
L
⎡
⎢⎢⎢⎢⎢⎢⎢⎢⎢⎢⎣
12Iz/L2
0
0
6Iz/L
−12Iz/L2
0
0
6Iz/L
0
12Iz/L2
−6Iy/L
0
0
−12Iy/L2
−6Iy/L
0
0
−6Iy/L
4Iy
0
0
6Iy/L
2Iy
0
6Iz/L
0
0
4Iz
−6Iz/L
0
0
2Iz
−12Iz/L2
0
0
−6Iz/L
12Iz/L2
0
0
−6Iz/L
0
−12Iy/L2
6Iy/L
0
0
12Iy/L2
6Iy/L
0
0
−6Iy/L
2Iy
0
0
6Iy/L
4Iy
0
6Iz/L
0
0
2Iz
−6Iz/L
0
0
4Iz
⎤
⎥⎥⎥⎥⎥⎥⎥⎥⎥⎥⎦
(29)
Me = ρ AL
420
⎡
⎢⎢⎢⎢⎢⎢⎢⎢⎢⎢⎣
156
0
0
22L
54
0
0
−13L
0
156
−22L
0
0
54
13L
0
0
−22L
4L2
0
0
−13L
−3L2
0
22L
0
0
4L2
13L
0
0
−3L2
54
0
0
13L
156
0
0
−22L
0
54
−13L
0
0
156
22L
0
0
13L
−3L2
0
0
22L
4L2
0
−13L
0
0
−3L2
−22L
0
0
4L2
⎤
⎥⎥⎥⎥⎥⎥⎥⎥⎥⎥⎦
(30)
where E0 is the stiffness, L is the length of the element, ρ is the mass density, A is the cross-sectional area and Iy
and Iz are the area moments for the y and z axes, respectively. For the sake of clarity and to relate with the previous
section, both variables form the vector of variables x = [Iy, Iz]. These last two parameters, the inertia moments,
are the variables with respect to which the problem will be differentiated. In the case of a square section both area
moments Iy and Iz are identical, causing the multiplicity of the eigenvalues.
The global stiffness and mass matrices are constructed by assembling the element matrices Ke and Me of both
elements:
K =
2
∑
e=1
Ke(Iy, Iz),
M =
2
∑
e=1
Me.
(31)
The eigenproblem is
{(K −λ jM)U j = 0,
j = 1, . . . , 8
UT
i MU j = δi j,
i, j = 1, . . . , 8 ,
(32)


350
D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
Fig. 4. Two-element cantilever.
where λ j are the eigenvalues, i.e. the square of the natural frequencies, and U j the mode shapes, that store the rotations
and displacements of the structure,
U = [v1, w1, θy1, θz1, v2, w2, θy2, θz2]T .
(33)
Set E = 1000, A = 1 and L = ρ = 1. When Iy = Iz = 1 in Eq. (32), two first eigenvalues are equal, so that we have
a double eigenvalue λ1 = λ2 = 1.8414, and a computed eigenvector basis collected in the matrix U,
U =
⎡
⎢⎢⎢⎢⎢⎢⎢⎢⎢⎢⎣
−0.0369
0.0584
−0.0584
−0.0369
−0.0402
−0.0254
0.0254
−0.0402
−0.0125
0.0198
−0.0198
−0.0125
−0.0340
−0.0215
0.0215
−0.0340
⎤
⎥⎥⎥⎥⎥⎥⎥⎥⎥⎥⎦
.
(34)
Target eigenvectors are collected in matrix
˜Y, whose columns are linearly independent (and actually
M-orthonormal) eigenvectors associated to the double eigenvalue (and therefore may be obtained as linear
combinations of the vectors in U):
˜Y =
⎡
⎢⎢⎢⎢⎢⎢⎢⎢⎢⎢⎣
0.0488
0.0488
0.0488
−0.0488
0.0336
−0.0336
−0.0336
−0.0336
0.0166
0.0166
0.0166
−0.0166
0.0284
−0.0284
−0.0284
−0.0284
⎤
⎥⎥⎥⎥⎥⎥⎥⎥⎥⎥⎦
.
(35)
Now, the reference set of eigenvectors Y is obtained from ˜Y as the solution of the maximization principle (20).
Indeed, we get that the components of Y differ less that 10−8 from the corresponding components of ˜Y, so that with
such a small difference in this situation we may assume Y = ˜Y. The difference between both sets is related to how
the reference set ˜Y is defined. In this example ˜Y is obtained by the inclusion of a small perturbance in the variables.
Since this perturbation is very small (but big enough to separate the eigenvalues) both sets of eigenvector must be
very similar and therefore ˜Y almost M-orthonormal, but they will never be exactly the same because matrices K and
M change slightly with the change in the variables.


D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
351
Dailey’s method is used to compute the eigenvector derivatives with respect to Iy and Iz. Following the steps
described in Table 2, we arrive at
ΓIy =
[ 0.7071
0.7071
−0.7071
0.7071
]
,
ΓIz =
[−0.7071
0.7071
0.7071
0.7071
]
(36)
and
∂ZIy
∂Iy
=
⎡
⎢⎢⎢⎢⎢⎢⎢⎢⎢⎢⎣
0.0000
0.0000
−0.0021
0.0000
−0.0051
0.0000
0.0000
0.0000
0.0000
0.0000
0.0012
0.0000
0.0020
0.0000
0.0000
0.0000
⎤
⎥⎥⎥⎥⎥⎥⎥⎥⎥⎥⎦
,
∂ZIz
∂Iz
=
⎡
⎢⎢⎢⎢⎢⎢⎢⎢⎢⎢⎣
0.0000
−0.0021
0.0000
0.0000
0.0000
0.0000
0.0000
0.0051
0.0000
0.0012
0.0000
0.0000
0.0000
0.0000
0.0000
−0.0020
⎤
⎥⎥⎥⎥⎥⎥⎥⎥⎥⎥⎦
.
(37)
Notice that the rotation matrices for obtaining the adjacent eigenvectors (ZIy, ZIz) are different for each variable, that
is, ΓIy ̸= ΓIz. Finally, following procedure given in Table 4, we obtain that the partial derivatives of the eigenmodes
given by Y are
∂Y
∂Iy
= ∂ZIy
∂Iy
ΓT
Iy =
⎡
⎢⎢⎢⎢⎢⎢⎢⎢⎢⎢⎣
0.0000
0.0000
−0.0015
0.0015
−0.0036
0.0036
0.0000
0.0000
0.0000
0.0000
0.0008
−0.0008
0.0014
−0.0014
0.0000
0.0000
⎤
⎥⎥⎥⎥⎥⎥⎥⎥⎥⎥⎦
,
∂Y
∂Iz
= ∂ZIz
∂Iz
ΓT
Iz =
⎡
⎢⎢⎢⎢⎢⎢⎢⎢⎢⎢⎣
0.0015
−0.0015
0.0000
0.0000
0.0000
0.0000
−0.0036
0.0036
−0.0008
0.0008
0.0000
0.0000
0.0000
0.0000
0.0014
−0.0014
⎤
⎥⎥⎥⎥⎥⎥⎥⎥⎥⎥⎦
.
(38)
As we did in the above example, we compute these derivatives by numerical differentiation and check that the
results coincide with those obtained with our analytical method. The first order backward formula used to compute
numerically the derivatives with respect to both variables Iy and Iz is expressed as follows:
∂NY
∂Iy
=
YIy −YI −
y
hN
,
∂NY
∂Iz
=
YIz −YI −
z
hN
,
(39)
where hN is the step, ∂NY/∂Iy and ∂NY/∂Iz are the numerically computed eigenvector derivatives and YI −
y and YI −
z
are the set of eigenvectors obtained by solving Eq. (32) when the variables Iy and Iz (for the upper element) are
perturbed as follows: I −
y = Iy −hN and I −
z
= Iz −hN. The value of these numerically computed derivatives for
hN = 10−3 is
∂NY
∂Iy
=
⎡
⎢⎢⎢⎢⎢⎢⎢⎢⎢⎢⎣
0.0000
0.0000
−0.0015
0.0015
−0.0036
0.0036
0.0000
0.0000
0.0000
0.0000
0.0008
−0.0008
0.0014
−0.0014
0.0000
0.0000
⎤
⎥⎥⎥⎥⎥⎥⎥⎥⎥⎥⎦
,
∂NY
∂Iz
=
⎡
⎢⎢⎢⎢⎢⎢⎢⎢⎢⎢⎣
0.0015
−0.0015
0.0000
0.0000
0.0000
0.0000
−0.0036
0.0036
−0.0008
0.0008
0.0000
0.0000
0.0000
0.0000
0.0014
−0.0014
⎤
⎥⎥⎥⎥⎥⎥⎥⎥⎥⎥⎦
.
(40)
The difference between the analytically and the numerically computed eigenvectors derivatives is smaller than
0.01%, showing the validity of the proposed method.
4. Application to optimization problems
The goal of our procedure is to compute sensitivities of functionals depending on eigenvectors appearing in
optimization problems, either in the cost or the constraints, or both of them. In this section we analyze an example
of an eigenmode optimization problem, showing how our procedure for computing eigenmode sensitivities succeeds


352
D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
Fig. 5. Design domain.
in applying a gradient-based optimization algorithm. The algorithm chosen to test our claim is MMA, the Method
of Moving Asymptotes [25], of common use in topology optimization problems. We carry out this validation with a
complex example in which both cost and constraint depend on eigenvectors. The example is the optimal design of
modal piezoelectric transducers [26]. This problem has already been analyzed and studied in [9,10], and here it is
used in order to illustrate how our method works out.
The problem is the following:
max
ρs,ρ p,α : Fk −α
(41)
subject to
(K −µ jM)Φ j = 0,
j = 1, . . . , J
ΦT
j MΦl = 0,
j,l = 1, . . . , J,
j ̸= l
ΦT
j Φ j = 1,
j = 1, . . . , J
|Fj| ≤α,
j = 1, . . . , J,
j ̸= k
ρs ∈[0, 1]
ρ p ∈[0, 1]
α ≥0.
(42)
The coefficient Fj is
Fj = CT Φ j,
(43)
with
C = R(ρs)(2ρ p −1)B,
(44)
where R is an interpolation function that models the piezoelectric effect in empty areas, ρs is the structural density
variable, ρ p is the electrode profile and B is the typical FE strain–displacement matrix. Φ j is the jth mode shape, µ j is
the jth eigenvalue, K and M are the global stiffness and mass matrices, respectively, and α is an independent auxiliary
variable used to model the problem. For details on the modeling the interested reader is referred to [9] and [10].
Coefficient Fj models the charge collected by the electrodes for the jth mode shape, up to a piezoelectric constant.
Then the objective of the problem is maximizing the charge collected for the mode shape of interest while the charge
of the rest of mode shapes is suppressed as much as possible.
We consider the case of a square domain clamped at its four corners as shown in Fig. 5. The number of mode shapes
used in the problem is J = 4. Young’s modulus is set to E = 167 GPa, Poisson’s ratio ν = 0.3, length L = 1m and
thickness t = 0.01m. First four mode shapes are represented in Fig. 6. Setting k = 1 the first mode shape is isolated
from the rest. This means that the coefficient F1 is maximized while coefficients F2, F3 and F4 are minimized.
Now we would like to remark what ordering in the mode shapes means. We take as target mode shapes those of the
whole square plate, when in a certain iteration we have a structure layout ρs, we compute the modes, and take those
closest to the first, second, third and fourth target mode shapes. Since the algorithm is iterative, this has to be done
at any iteration, being computationally costly, but preventing mode switching (change of order of eigenfrequencies in


D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
353
(a) Y1, fr1 = 1072 Hz.
(b) Y2, fr2 = 1072 Hz.
(c) Y3, fr3 = 1268 Hz.
(d)
Y4,
fr4 = 3742 Hz.
Fig. 6. Mode shapes of the plate.
(a) ¯Y1.
(b) ¯Y2.
(c) ¯Y3.
(d) ¯Y4.
(e) ¯Y5.
(f) ¯Y6.
(g) ¯Y7.
(h) ¯Y8.
Fig. 7. Mode shapes computed at ith iteration step.
the structure spectrum). The way we select the closest modes is by the modal assurance criterion, MAC, or its variant
for multiple selection introduced in the previous section through the maximization principle (20). At any iteration, a
set of ˜J eigenvectors, where ˜J > J has to be computed and among those select the one whose inner product with the
kth target mode shape is closest to one, and this will be the k-eigenvector for the actual iteration. Since, mode shapes
and target mode shapes are normalized to be unitary (euclidean norm equal to 1), their inner product will be smaller
than or equal to one, and it gets maximal when both vectors are equal. Fig. 6 shows the target mode shapes (the first
four mode shapes of the whole plate), and in Fig. 7 we see the first eight mode shapes in a disordered way, and in
Table 5 how through the MAC method they are assigned in the right way. We refer readers to [20] for an explanation
of MAC, and to [9,10] for a complete exposition of the use of MAC in this situation. Mode tracking is imperative
in this sort of problems, otherwise the mode shapes that are being optimized and suppressed would change in each
iteration jeopardizing the convergence of the iterative method.


354
D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
Table 5
MAC for mode shapes of reference.
(a) First mode shape.
(b) Second mode shape.
(c) Third mode shape.
(d) Fourth mode shape.
Fig. 8. Mode shape of reference Y (left) and computed at the first iteration step U (right).
Coming back to our problem, note that the first and the second mode shapes present the same eigenfrequency in the
first iteration, and then the derivatives of F1 and F2, that depend on the eigenvectors Φ1 and Φ2, must be computed
by using the new method proposed in the previous section. During the iterative optimization procedure eigenvalues
will split out and become simple, and on the other hand other eigenvalues will coalesce and become double during
one iteration.
The reference mode shapes obtained in the first iteration are shown in Fig. 8.
In this case, it is easy to identify the mode shapes. The eigenfrequency for the first and second modes is repeated,
and then the basis of eigenvectors is not unique. Before computing the derivatives, the finite dimensional optimization


D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
355
Fig. 9. Structure density (left) and polarization profile (right) when the first mode shape is isolated from the first 4 modes.
Fig. 10. Evolution of the cost.
Fig. 11. Structure density (left) and polarization profile (right) when the second mode shape is isolated from the first 4 modes.
problem proposed in the previous section must be solved. The derivatives of F3 and F4 are computed by using Nelson’s
method, and the derivatives of F1 and F2 with the new method proposed.
Fig. 9 shows the results of the optimization problem. Fig. 9 left shows the structure density, where black and white
mean solid and void areas, respectively. Fig. 9 right shows the polarization profile, where cyan and orange colors
represent areas of the structure covered by positive and negative electrodes, respectively.
The evolution of the objective function is shown in Fig. 10. It is noticed that the cost converges in less than 100
iterations. The initial point of the iterative process is the optimized electrode of the mode shape of interest for the
homogeneous plate.
A second example is presented in Fig. 11, where the second mode shape is isolated. It is shown in Fig. 8b that the
plate moves in the direction which is a linear combination of the movements on the x- and y-axes. Nevertheless, at the
end of the iterative process, the solution (optimized electrode profile) presents a polarity that coincides with the mode
shape of reference Y2, in other words, the jumps between positive and negative polarity coincides with the parts of
the structure that are subject to traction and compression in the reference mode shape Y2. A summary of the process
is shown in Table 6.


356
D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
Table 6
Steps of the optimization process.
1. Set the constants of the problem: stiffness, thickness, Poisson’s
ratio and volume density.
2. Select the J mode shapes of reference.
3. Initialize both design variables ρs and ρ p.
4. Compute the first ˜Jth eigenmodes of the plate and identify the
Jth closest modes to the reference by means of MAC.
5. Check the multiplicity of the eigenvalues.
• If it is simple compute the coefficients Fj and their
sensitivities by using Nelson’s method.
• If it is multiple proceed in the following way:
– Find a new basis of orthonormal eigenvectors as solution of
the finite dimensional optimization problem presented in Eq. (20).
This provides the reference set of eigenvectors.
– Compute the coefficients Fj and their sensitivities by using
the new method proposed in this work.
6. Update the new set of eigenvectors of reference, replacing the
previous one with the new set computed (if needed).
7. Update the design variables ρs and ρ p by using MMA.
8. Until convergence, go back to step 4.
5. Conclusions
In this paper, we study eigenmode optimization problems from a general framework perspective whenever tracking
specific mode shapes. The main questions we address are: mode shape selection, eigenmode differentiability and
eigenmode derivative calculation. We present a novel method for mode shape selection very close, and in the spirit of
the MAC (modal assurance criterion) but also considering the possibility of multiple selection, what is necessary in the
case of mode shapes associated to multiple eigenvalues. For those selected mode shapes, which in general differ from
the adjacent eigenmodes, we propose a simple algorithm, that takes advantage of the linear structure of eigenspaces,
for computing their derivatives. Those derivatives are required by any gradient-based optimization method. A review
on the existing mathematical results on eigenvector differentiability is given, including a result in [24] that gives
theoretical validity to our method. Further, the success of our algorithm is numerically corroborated with three
examples: two structural analysis examples in which the algorithm for derivatives computation is numerically
validated comparing with the results obtained via numerical differentiation; and an optimization example in which
both cost and constraints depend on eigenmodes associated to multiple eigenvalues, and for which the optimization
MMA algorithm together with our selection mode shape and computation of derivatives procedures succeed in
reaching optimal solutions.
Acknowledgments
We appreciate very much the comments and suggestions of an anonymous referee that considerably improved the
quality of the manuscript. This work has been funded by MINECO (Spain) through grant MTM2013-47053-P and
Junta de Comunidades de Castilla-La Mancha (Spain) through grant PEII-2014-010-P.
References
[1] M.P. Bendsøe, O. Sigmund, Topology Optimization: Theory, Methods and Applications, second ed., Springer, 2003.
[2] E.J. Haug, K.K. Choi, V. Komkov, Design Sensitivity Analysis of Structural Systems, Academic Press, 1986.
[3] A.P. Seyranian, E. Lund, N. Olhoff, Multiple eigenvalues in structural optimization problems, Struct. Multidiscip. Optim. 8 (1994) 207–227.
[4] J. Du, N. Olhoff, Topological design of freely vibrating continuum structures for maximum values of simple and multiple eigenfrequencies
and frequency gaps, Struct. Multidiscip. Optim. 34 (2) (2007) 91–110.
[5] L.V. Hansen, Topology optimization of free vibrations of fiber laser packages, Struct. Multidiscip. Optim. 29 (5) (2005) 341–348.
[6] Y. Maeda, S. Nishiwaki, K. Izui, M. Yoshimura, K. Matsui, K. Terada, Structural topology optimization of vibrating structures with specified
eigenfrequencies and eigenmode shapes, Int. J. Number Methods Eng. 67 (5) (2006) 597–628.
[7] P.H. Nakasone, E.C.N. Silva, Dynamic design of piezoelectric laminated sensors and actuators using topology optimization, J. Intell. Mater.
Syst. Struct. 21 (16) (2010) 1627–1652.


D. Ruiz et al. / Comput. Methods Appl. Mech. Engrg. 326 (2017) 338–357
357
[8] T.D. Tsai, C.C. Cheng, Structural design for desired eigenfrequencies and mode shapes using topology optimization, Struct. Multidiscip.
Optim. 47 (5) (2013) 673–686.
[9] D. Ruiz, J.C. Bellido, A. Donoso, Design of piezoelectric modal filters by simultaneously optimizing the structure layout and the electrode
profile, Struct. Multidiscip. Optim. 53 (2016) 715–730.
[10] D. Ruiz, J.C. Bellido, A. Donoso, Optimal design of piezoelectric modal transducers, Arch. Comput. Methods Eng. (2016). http://dx.doi.org/
10.1007/s11831-016-9200-5.
[11] R.L. Dailey, Eigenvector derivatives with repeated eigenvalues, AIAA J. 27 (4) (1987) 486–491.
[12] R.L. Fox, M.P. Kapoor, Rates of change of eigenvalues and eigenvectors, AIAA J. 6 (12) (1968) 2426–2429.
[13] M.I. Friswell, The derivatives of repeated eigenvalues and their associated eigenvectors, J. Vib. Acoust. 118 (3) (1996) 390–397.
[14] X.Y. Long, C. Jiang, X. Han, New method for eigenvector-sensitivity analysis with repeated eigenvalues and eigenvalue derivatives, AIAA J.
53 (5) (2015) 1226–1235.
[15] I. Lee, Numerical method for sensitivity analysis of eigensystems with non-repeated and repeated eigenvalues, J. Sound Vib. 195 (1) (1996)
17–32.
[16] R.B. Nelson, Simplified calculation of eigenvector derivatives, AIAA J. 14 (9) (1976) 1201–1205.
[17] I.U. Ojalvo, Efficient computation of mode-shape derivatives for large dynamic systems, AIAA J. 25 (10) (1987) 1386–1390.
[18] N.P. van der Aa, H.G. ter Morsche, R.R.M. Mattheij, Computation of eigenvalue and eigenvector derivatives for a general complex-valued
eigensystem, Electron. J. Linear Algebra (16) (2007) 300–314.
[19] B.P. Wang, Improved approximate methods for computing eigenvector derivatives in structural dynamics, AIAA J. (6) (1991) 1018–1020.
[20] T.S. Kim, Y.Y. Kim, MAC-based mode-tracking in structural topology optimization, Comput. Struct. 74 (3) (2000) 375–383.
[21] J.R. Magnus, On differentiating eigenvalues and eigenvectors, Econometric Theory (1) (1985) 179–191.
[22] D. Tcherniak, Topology optimization of resonating structures using SIMP method, Int. J. Number Methods Eng. 54 (11) (2002) 1605–1622.
[23] F.H. Clarke, Optimization and Nonsmooth Analysis, SIAM, 1990.
[24] T. Kato, Perturbation Theory of Linear Operators, Springer, Reprint of the 1980 edition.
[25] K. Svanberg, The method of moving asymptotes-a new method for structural optimization, Int. J. Number Methods Eng. 24 (2) (1987)
359–373.
[26] C.K. Lee, F.C. Moon, Modal sensors/actuators, J. Appl. Mech. 57 (2) (1990) 434–441.



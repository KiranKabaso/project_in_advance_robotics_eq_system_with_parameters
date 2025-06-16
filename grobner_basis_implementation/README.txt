======================================================
README: Attempted Grobner Basis Implementation
======================================================

Overview
------------------------------------------------------
This component attempted to solve parametric polynomial systems  
using a standard Grobner basis approach. The implementation was  
done from scratch and tested on various cases. It was successful for:

• **Very simple parametric cases** (e.g., low-degree, few variables).  
• **Non-parametric cases**, where all coefficients were constant.

However, the method failed to scale and was ultimately abandoned  
in favor of the Grobner Cover method.

Limitations Discovered
------------------------------------------------------
The Grobner basis method quickly became infeasible as soon as  
nontrivial parameter interactions were introduced. Without any  
form of parametric space partitioning, the generated bases  
included extremely large symbolic coefficients in an attempt to  
account for all parameter values simultaneously — making  
computation and interpretation both impractical.

Theoretical Background and Reference
------------------------------------------------------
To support this implementation, I read the first **100 pages**  
of the book:

**Ideals, Varieties, and Algorithms**  
By: David A. Cox, John Little, Donal O'Shea (Fourth Edition)

Despite the detailed foundational content, the book did not  
provide tools suitable for handling **parametric equation systems**  
in general, which led to the transition toward the Grobner Cover  
framework.

Conclusion
------------------------------------------------------
Due to these theoretical and computational limitations, the Grobner  
basis approach was **abandoned** and replaced with a Grobner Cover–based  
pipeline (implemented via Singular’s `grobcov.lib`) which successfully  
partitions the parameter space and handles symbolic systems as  
needed.

			 ============================
			 LINUX KERNEL MEMORY BARRIERS
			 ============================

By: David Howells <dhowells@redhat.com>
    Paul E. McKenney <paulmck@linux.vnet.ibm.com>
    Will Deacon <will.deacon@arm.com>
    Peter Zijlstra <peterz@infradead.org>

==========
DISCLAIMER
==========

This document is not a specification; it is intentionally (for the sake of
brevity) and unintentionally (due to being human) incomplete. This document is
meant as a guide to using the various memory barriers provided by Linux, but
in case of any doubt (and there are many) please ask.

To repeat, this document is not a specification of what Linux expects from
hardware.

The purpose of this document is twofold:

 (1) to specify the minimum functionality that one can rely on for any
     particular barrier, and

 (2) to provide a guide as to how to use the barriers that are available.

Note that an architecture can provide more than the minimum requirement
for any particular barrier, but if the architecture provides less than
that, that architecture is incorrect.

Note also that it is possible that a barrier may be a no-op for an
architecture because the way that arch works renders an explicit barrier
unnecessary in that case.


========
CONTENTS
========

 (*) Abstract memory access model.

     - Device operations.
     - Guarantees.

 (*) What are memory barriers?

     - Varieties of memory barrier.
     - What may not be assumed about memory barriers?
     - Data dependency barriers.
     - Control dependencies.
     - SMP barrier pairing.
     - Examples of memory barrier sequences.
     - Read memory barriers vs load speculation.
     - Transitivity

 (*) Explicit kernel barriers.

     - Compiler barrier.
     - CPU memory barriers.
     - MMIO write barrier.

 (*) Implicit kernel memory barriers.

     - Lock acquisition functions.
     - Interrupt disabling functions.
     - Sleep and wake-up functions.
     - Miscellaneous functions.

 (*) Inter-CPU acquiring barrier effects.

     - Acquires vs memory accesses.
     - Acquires vs I/O accesses.

 (*) Where are memory barriers needed?

     - Interprocessor interaction.
     - Atomic operations.
     - Accessing devices.
     - Interrupts.

 (*) Kernel I/O barrier effects.

 (*) Assumed minimum execution ordering model.

 (*) The effects of the cpu cache.

     - Cache coherency.
     - Cache coherency vs DMA.
     - Cache coherency vs MMIO.

 (*) The things CPUs get up to.

     - And then there's the Alpha.
     - Virtual Machine Guests.

 (*) Example uses.

     - Circular buffers.

 (*) References.


============================
ABSTRACT MEMORY ACCESS MODEL
============================

Consider the following abstract model of the system:

		            :                :
		            :                :
		            :                :
		+-------+   :   +--------+   :   +-------+
		|       |   :   |        |   :   |       |
		|       |   :   |        |   :   |       |
		| CPU 1 |<----->| Memory |<----->| CPU 2 |
		|       |   :   |        |   :   |       |
		|       |   :   |        |   :   |       |
		+-------+   :   +--------+   :   +-------+
		    ^       :       ^        :       ^
		    |       :       |        :       |
		    |       :       |        :       |
		    |       :       v        :       |
		    |       :   +--------+   :       |
		    |       :   |        |   :       |
		    |       :   |        |   :       |
		    +---------->| Device |<----------+
		            :   |        |   :
		            :   |        |   :
		            :   +--------+   :
		            :                :

Each CPU executes a program that generates memory access operations.  In the
abstract CPU, memory operation ordering is very relaxed, and a CPU may actually
perform the memory operations in any order it likes, provided program causality
appears to be maintained.  Similarly, the compiler may also arrange the
instructions it emits in any order it likes, provided it doesn't affect the
apparent operation of the program.

So in the above diagram, the effects of the memory operations performed by a
CPU are perceived by the rest of the system as the operations cross the
interface between the CPU and rest of the system (the dotted lines).


For example, consider the following sequence of events:

	CPU 1		CPU 2
	===============	===============
	{ A == 1; B == 2 }
	A = 3;		x = B;
	B = 4;		y = A;

The set of accesses as seen by the memory system in the middle can be arranged
in 24 different combinations:

	STORE A=3,	STORE B=4,	y=LOAD A->3,	x=LOAD B->4
	STORE A=3,	STORE B=4,	x=LOAD B->4,	y=LOAD A->3
	STORE A=3,	y=LOAD A->3,	STORE B=4,	x=LOAD B->4
	STORE A=3,	y=LOAD A->3,	x=LOAD B->2,	STORE B=4
	STORE A=3,	x=LOAD B->2,	STORE B=4,	y=LOAD A->3
	STORE A=3,	x=LOAD B->2,	y=LOAD A->3,	STORE B=4
	STORE B=4,	STORE A=3,	y=LOAD A->3,	x=LOAD B->4
	STORE B=4, ...
	...

and can thus result in four different combinations of values:

	x == 2, y == 1
	x == 2, y == 3
	x == 4, y == 1
	x == 4, y == 3


Furthermore, the stores committed by a CPU to the memory system may not be
perceived by the loads made by another CPU in the same order as the stores were
committed.


As a further example, consider this sequence of events:

	CPU 1		CPU 2
	===============	===============
	{ A == 1, B == 2, C == 3, P == &A, Q == &C }
	B = 4;		Q = P;
	P = &B		D = *Q;

There is an obvious data dependency here, as the value loaded into D depends on
the address retrieved from P by CPU 2.  At the end of the sequence, any of the
following results are possible:

	(Q == &A) and (D == 1)
	(Q == &B) and (D == 2)
	(Q == &B) and (D == 4)

Note that CPU 2 will never try and load C into D because the CPU will load P
into Q before issuing the load of *Q.


DEVICE OPERATIONS
-----------------

Some devices present their control interfaces as collections of memory
locations, but the order in which the control registers are accessed is very
important.  For instance, imagine an ethernet card with a set of internal
registers that are accessed through an address port register (A) and a data
port register (D).  To read internal register 5, the following code might then
be used:

	*A = 5;
	x = *D;

but this might show up as either of the following two sequences:

	STORE *A = 5, x = LOAD *D
	x = LOAD *D, STORE *A = 5

the second of which will almost certainly result in a malfunction, since it set
the address _after_ attempting to read the register.


GUARANTEES
----------

There are some minimal guarantees that may be expected of a CPU:

 (*) On any given CPU, dependent memory accesses will be issued in order, with
     respect to itself.  This means that for:

	Q = READ_ONCE(P); smp_read_barrier_depends(); D = READ_ONCE(*Q);

     the CPU will issue the following memory operations:

	Q = LOAD P, D = LOAD *Q

     and always in that order.  On most systems, smp_read_barrier_depends()
     does nothing, but it is required for DEC Alpha.  The READ_ONCE()
     is required to prevent compiler mischief.  Please note that you
     should normally use something like rcu_dereference() instead of
     open-coding smp_read_barrier_depends().

 (*) Overlapping loads and stores within a particular CPU will appear to be
     ordered within that CPU.  This means that for:

	a = READ_ONCE(*X); WRITE_ONCE(*X, b);

     the CPU will only issue the following sequence of memory operations:

	a = LOAD *X, STORE *X = b

     And for:

	WRITE_ONCE(*X, c); d = READ_ONCE(*X);

     the CPU will only issue:

	STORE *X = c, d = LOAD *X

     (Loads and stores overlap if they are targeted at overlapping pieces of
     memory).

And there are a number of things that _must_ or _must_not_ be assumed:

 (*) It _must_not_ be assumed that the compiler will do what you want
     with memory references that are not protected by READ_ONCE() and
     WRITE_ONCE().  Without them, the compiler is within its rights to
     do all sorts of "creative" transformations, which are covered in
     the COMPILER BARRIER section.

 (*) It _must_not_ be assumed that independent loads and stores will be issued
     in the order given.  This means that for:

	X = *A; Y = *B; *D = Z;

     we may get any of the following sequences:

	X = LOAD *A,  Y = LOAD *B,  STORE *D = Z
	X = LOAD *A,  STORE *D = Z, Y = LOAD *B
	Y = LOAD *B,  X = LOAD *A,  STORE *D = Z
	Y = LOAD *B,  STORE *D = Z, X = LOAD *A
	STORE *D = Z, X = LOAD *A,  Y = LOAD *B
	STORE *D = Z, Y = LOAD *B,  X = LOAD *A

 (*) It _must_ be assumed that overlapping memory accesses may be merged or
     discarded.  This means that for:

	X = *A; Y = *(A + 4);

     we may get any one of the following sequences:

	X = LOAD *A; Y = LOAD *(A + 4);
	Y = LOAD *(A + 4); X = LOAD *A;
	{X, Y} = LOAD {*A, *(A + 4) };

     And for:

	*A = X; *(A + 4) = Y;

     we may get any of:

	STORE *A = X; STORE *(A + 4) = Y;
	STORE *(A + 4) = Y; STORE *A = X;
	STORE {*A, *(A + 4) } = {X, Y};

And there are anti-guarantees:

 (*) These guarantees do not apply to bitfields, because compilers often
     generate code to modify these using non-atomic read-modify-write
     sequences.  Do not attempt to use bitfields to synchronize parallel
     algorithms.

 (*) Even in cases where bitfields are protected by locks, all fields
     in a given bitfield must be protected by one lock.  If two fields
     in a given bitfield are protected by different locks, the compiler's
     non-atomic read-modify-write sequences can cause an update to one
     field to corrupt the value of an adjacent field.

 (*) These guarantees apply only to properly aligned and sized scalar
     variables.  "Properly sized" currently means variables that are
     the same size as "char", "short", "int" and "long".  "Properly
     aligned" means the natural alignment, thus no constraints for
     "char", two-byte alignment for "short", four-byte alignment for
     "int", and either four-byte or eight-byte alignment for "long",
     on 32-bit and 64-bit systems, respectively.  Note that these
     guarantees were introduced into the C11 standard, so beware when
     using older pre-C11 compilers (for example, gcc 4.6).  The portion
     of the standard containing this guarantee is Section 3.14, which
     defines "memory location" as follows:

     	memory location
		either an object of scalar type, or a maximal sequence
		of adjacent bit-fields all having nonzero width

		NOTE 1: Two threads of execution can update and access
		separate memory locations without interfering with
		each other.

		NOTE 2: A bit-field and an adjacent non-bit-field member
		are in separate memory locations. The same applies
		to two bit-fields, if one is declared inside a nested
		structure declaration and the other is not, or if the two
		are separated by a zero-length bit-field declaration,
		or if they are separated by a non-bit-field member
		declaration. It is not safe to concurrently update two
		bit-fields in the same structure if all members declared
		between them are also bit-fields, no matter what the
		sizes of those intervening bit-fields happen to be.


=========================
WHAT ARE MEMORY BARRIERS?
=========================

As can be seen above, independent memory operations are effectively performed
in random order, but this can be a problem for CPU-CPU interaction and for I/O.
What is required is some way of intervening to instruct the compiler and the
CPU to restrict the order.

Memory barriers are such interventions.  They impose a perceived partial
ordering over the memory operations on either side of the barrier.

Such enforcement is important because the CPUs and other devices in a system
can use a variety of tricks to improve performance, including reordering,
deferral and combination of memory operations; speculative loads; speculative
branch prediction and various types of caching.  Memory barriers are used to
override or suppress these tricks, allowing the code to sanely control the
interaction of multiple CPUs and/or devices.


VARIETIES OF MEMORY BARRIER
---------------------------

Memory barriers come in four basic varieties:

 (1) Write (or store) memory barriers.

     A write memory barrier gives a guarantee that all the STORE operations
     specified before the barrier will appear to happen before all the STORE
     operations specified after the barrier with respect to the other
     components of the system.

     A write barrier is a partial ordering on stores only; it is not required
     to have any effect on loads.

     A CPU can be viewed as committing a sequence of store operations to the
     memory system as time progresses.  All stores before a write barrier will
     occur in the sequence _before_ all the stores after the write barrier.

     [!] Note that write barriers should normally be paired with read or data
     dependency barriers; see the "SMP barrier pairing" subsection.


 (2) Data dependency barriers.

     A data dependency barrier is a weaker form of read barrier.  In the case
     where two loads are performed such that the second depends on the result
     of the first (eg: the first load retrieves the address to which the second
     load will be directed), a data dependency barrier would be required to
     make sure that the target of the second load is updated before the address
     obtained by the first load is accessed.

     A data dependency barrier is a partial ordering on interdependent loads
     only; it is not required to have any effect on stores, independent loads
     or overlapping loads.

     As mentioned in (1), the other CPUs in the system can be viewed as
     committing sequences of stores to the memory system that the CPU being
     considered can then perceive.  A data dependency barrier issued by the CPU
     under consideration guarantees that for any load preceding it, if that
     load touches one of a sequence of stores from another CPU, then by the
     time the barrier completes, the effects of all the stores prior to that
     touched by the load will be perceptible to any loads issued after the data
     dependency barrier.

     See the "Examples of memory barrier sequences" subsection for diagrams
     showing the ordering constraints.

     [!] Note that the first load really has to have a _data_ dependency and
     not a control dependency.  If the address for the second load is dependent
     on the first load, but the dependency is through a conditional rather than
     actually loading the address itself, then it's a _control_ dependency and
     a full read barrier or better is required.  See the "Control dependencies"
     subsection for more information.

     [!] Note that data dependency barriers should normally be paired with
     write barriers; see the "SMP barrier pairing" subsection.


 (3) Read (or load) memory barriers.

     A read barrier is a data dependency barrier plus a guarantee that all the
     LOAD operations specified before the barrier will appear to happen before
     all the LOAD operations specified after the barrier with respect to the
     other components of the system.

     A read barrier is a partial ordering on loads only; it is not required to
     have any effect on stores.

     Read memory barriers imply data dependency barriers, and so can substitute
     for them.

     [!] Note that read barriers should normally be paired with write barriers;
     see the "SMP barrier pairing" subsection.


 (4) General memory barriers.

     A general memory barrier gives a guarantee that all the LOAD and STORE
     operations specified before the barrier will appear to happen before all
     the LOAD and STORE operations specified after the barrier with respect to
     the other components of the system.

     A general memory barrier is a partial ordering over both loads and stores.

     General memory barriers imply both read and write memory barriers, and so
     can substitute for either.


And a couple of implicit varieties:

 (5) ACQUIRE operations.

     This acts as a one-way permeable barrier.  It guarantees that all memory
     operations after the ACQUIRE operation will appear to happen after the
     ACQUIRE operation with respect to the other components of the system.
     ACQUIRE operations include LOCK operations and both smp_load_acquire()
     and smp_cond_acquire() operations. The later builds the necessary ACQUIRE
     semantics from relying on a control dependency and smp_rmb().

     Memory operations that occur before an ACQUIRE operation may appear to
     happen after it completes.

     An ACQUIRE operation should almost always be paired with a RELEASE
     operation.


 (6) RELEASE operations.

     This also acts as a one-way permeable barrier.  It guarantees that all
     memory operations before the RELEASE operation will appear to happen
     before the RELEASE operation with respect to the other components of the
     system. RELEASE operations include UNLOCK operations and
     smp_store_release() operations.

     Memory operations that occur after a RELEASE operation may appear to
     happen before it completes.

     The use of ACQUIRE and RELEASE operations generally precludes the need
     for other sorts of memory barrier (but note the exceptions mentioned in
     the subsection "MMIO write barrier").  In addition, a RELEASE+ACQUIRE
     pair is -not- guaranteed to act as a full memory barrier.  However, after
     an ACQUIRE on a given variable, all memory accesses preceding any prior
     RELEASE on that same variable are guaranteed to be visible.  In other
     words, within a given variable's critical section, all accesses of all
     previous critical sections for that variable are guaranteed to have
     completed.

     This means that ACQUIRE acts as a minimal "acquire" operation and
     RELEASE acts as a minimal "release" operation.

A subset of the atomic operations described in atomic_t.txt have ACQUIRE and
RELEASE variants in addition to fully-ordered and relaxed (no barrier
semantics) definitions.  For compound atomics performing both a load and a
store, ACQUIRE semantics apply only to the load and RELEASE semantics apply
only to the store portion of the operation.

Memory barriers are only required where there's a possibility of interaction
between two CPUs or between a CPU and a device.  If it can be guaranteed that
there won't be any such interaction in any particular piece of code, then
memory barriers are unnecessary in that piece of code.


Note that these are the _minimum_ guarantees.  Different architectures may give
more substantial guarantees, but they may _not_ be relied upon outside of arch
specific code.


WHAT MAY NOT BE ASSUMED ABOUT MEMORY BARRIERS?
----------------------------------------------

There are certain things that the Linux kernel memory barriers do not guarantee:

 (*) There is no guarantee that any of the memory accesses specified before a
     memory barrier will be _complete_ by the completion of a memory barrier
     instruction; the barrier can be considered to draw a line in that CPU's
     access queue that accesses of the appropriate type may not cross.

 (*) There is no guarantee that issuing a memory barrier on one CPU will have
     any direct effect on another CPU or any other hardware in the system.  The
     indirect effect will be the order in which the second CPU sees the effects
     of the first CPU's accesses occur, but see the next point:

 (*) There is no guarantee that a CPU will see the correct order of effects
     from a second CPU's accesses, even _if_ the second CPU uses a memory
     barrier, unless the first CPU _also_ uses a matching memory barrier (see
     the subsection on "SMP Barrier Pairing").

 (*) There is no guarantee that some intervening piece of off-the-CPU
     hardware[*] will not reorder the memory accesses.  CPU cache coherency
     mechanisms should propagate the indirect effects of a memory barrier
     between CPUs, but might not do so in order.

	[*] For information on bus mastering DMA and coherency please read:

	    Documentation/PCI/pci.txt
	    Documentation/DMA-API-HOWTO.txt
	    Documentation/DMA-API.txt


DATA DEPENDENCY BARRIERS
------------------------

The usage requirements of data dependency barriers are a little subtle, and
it's not always obvious that they're needed.  To illustrate, consider the
following sequence of events:

	CPU 1		      CPU 2
	===============	      ===============
	{ A == 1, B == 2, C == 3, P == &A, Q == &C }
	B = 4;
	<write barrier>
	WRITE_ONCE(P, &B)
			      Q = READ_ONCE(P);
			      D = *Q;

There's a clear data dependency here, and it would seem that by the end of the
sequence, Q must be either &A or &B, and that:

	(Q == &A) implies (D == 1)
	(Q == &B) implies (D == 4)

But!  CPU 2's perception of P may be updated _before_ its perception of B, thus
leading to the following situation:

	(Q == &B) and (D == 2) ????

Whilst this may seem like a failure of coherency or causality maintenance, it
isn't, and this behaviour can be observed on certain real CPUs (such as the DEC
Alpha).

To deal with this, a data dependency barrier or better must be inserted
between the address load and the data load:

	CPU 1		      CPU 2
	===============	      ===============
	{ A == 1, B == 2, C == 3, P == &A, Q == &C }
	B = 4;
	<write barrier>
	WRITE_ONCE(P, &B);
			      Q = READ_ONCE(P);
			      <data dependency barrier>
			      D = *Q;

This enforces the occurrence of one of the two implications, and prevents the
third possibility from arising.


[!] Note that this extremely counterintuitive situation arises most easily on
machines with split caches, so that, for example, one cache bank processes
even-numbered cache lines and the other bank processes odd-numbered cache
lines.  The pointer P might be stored in an odd-numbered cache line, and the
variable B might be stored in an even-numbered cache line.  Then, if the
even-numbered bank of the reading CPU's cache is extremely busy while the
odd-numbered bank is idle, one can see the new value of the pointer P (&B),
but the old value of the variable B (2).


A data-dependency barrier is not required to order dependent writes
because the CPUs that the Linux kernel supports don't do writes
until they are certain (1) that the write will actually happen, (2)
of the location of the write, and (3) of the value to be written.
But please carefully read the "CONTROL DEPENDENCIES" section and the
Documentation/RCU/rcu_dereference.txt file:  The compiler can and does
break dependencies in a great many highly creative ways.

	CPU 1		      CPU 2
	===============	      ===============
	{ A == 1, B == 2, C = 3, P == &A, Q == &C }
	B = 4;
	<write barrier>
	WRITE_ONCE(P, &B);
			      Q = READ_ONCE(P);
			      WRITE_ONCE(*Q, 5);

Therefore, no data-dependency barrier is required to order the read into
Q with the store into *Q.  In other words, this outcome is prohibited,
even without a data-dependency barrier:

	(Q == &B) && (B == 4)

Please note that this pattern should be rare.  After all, the whole point
of dependency ordering is to -prevent- writes to the data structure, along
with the expensive cache misses associated with those writes.  This pattern
can be used to record rare error conditions and the like, and the CPUs'
naturally occurring ordering prevents such records from being lost.


The data dependency barrier is very important to the RCU system,
for example.  See rcu_assign_pointer() and rcu_dereference() in
include/linux/rcupdate.h.  This permits the current target of an RCU'd
pointer to be replaced with a new modified target, without the replacement
target appearing to be incompletely initialised.

See also the subsection on "Cache Coherency" for a more thorough example.


CONTROL DEPENDENCIES
--------------------

Control dependencies can be a bit tricky because current compilers do
not understand them.  The purpose of this section is to help you prevent
the compiler's ignorance from breaking your code.

A load-load control dependency requires a full read memory barrier, not
simply a data dependency barrier to make it work correctly.  Consider the
following bit of code:

	q = READ_ONCE(a);
	if (q) {
		<data dependency barrier>  /* BUG: No data dependency!!! */
		p = READ_ONCE(b);
	}

This will not have the desired effect because there is no actual data
dependency, but rather a control dependency that the CPU may short-circuit
by attempting to predict the outcome in advance, so that other CPUs see
the load from b as having happened before the load from a.  In such a
case what's actually required is:

	q = READ_ONCE(a);
	if (q) {
		<read barrier>
		p = READ_ONCE(b);
	}

However, stores are not speculated.  This means that ordering -is- provided
for load-store control dependencies, as in the following example:

	q = READ_ONCE(a);
	if (q) {
		WRITE_ONCE(b, 1);
	}

Control dependencies pair normally with other types of barriers.
That said, please note that neither READ_ONCE() nor WRITE_ONCE()
are optional! Without the READ_ONCE(), the compiler might combine the
load from 'a' with other loads from 'a'.  Without the WRITE_ONCE(),
the compiler might combine the store to 'b' with other stores to 'b'.
Either can result in highly counterintuitive effects on ordering.

Worse yet, if the compiler is able to prove (say) that the value of
variable 'a' is always non-zero, it would be well within its rights
to optimize the original example by eliminating the "if" statement
as follows:

	q = a;
	b = 1;  /* BUG: Compiler and CPU can both reorder!!! */

So don't leave out the READ_ONCE().

It is tempting to try to enforce ordering on identical stores on both
branches of the "if" statement as follows:

	q = READ_ONCE(a);
	if (q) {
		barrier();
		WRITE_ONCE(b, 1);
		do_something();
	} else {
		barrier();
		WRITE_ONCE(b, 1);
		do_something_else();
	}

Unfortunately, current compilers will transform this as follows at high
optimization levels:

	q = READ_ONCE(a);
	barrier();
	WRITE_ONCE(b, 1);  /* BUG: No ordering vs. load from a!!! */
	if (q) {
		/* WRITE_ONCE(b, 1); -- moved up, BUG!!! */
		do_something();
	} else {
		/* WRITE_ONCE(b, 1); -- moved up, BUG!!! */
		do_something_else();
	}

Now there is no conditional between the load from 'a' and the store to
'b', which means that the CPU is within its rights to reorder them:
The conditional is absolutely required, and must be present in the
assembly code even after all compiler optimizations have been applied.
Therefore, if you need ordering in this example, you need explicit
memory barriers, for example, smp_store_release():

	q = READ_ONCE(a);
	if (q) {
		smp_store_release(&b, 1);
		do_something();
	} else {
		smp_store_release(&b, 1);
		do_something_else();
	}

In contrast, without explicit memory barriers, two-legged-if control
ordering is guaranteed only when the stores differ, for example:

	q = READ_ONCE(a);
	if (q) {
		WRITE_ONCE(b, 1);
		do_something();
	} else {
		WRITE_ONCE(b, 2);
		do_something_else();
	}

The initial READ_ONCE() is still required to prevent the compiler from
proving the value of 'a'.

In addition, you need to be careful what you do with the local variable 'q',
otherwise the compiler might be able to guess the value and again remove
the needed conditional.  For example:

	q = READ_ONCE(a);
	if (q % MAX) {
		WRITE_ONCE(b, 1);
		do_something();
	} else {
		WRITE_ONCE(b, 2);
		do_something_else();
	}

If MAX is defined to be 1, then the compiler knows that (q % MAX) is
equal to zero, in which case the compiler is within its rights to
transform the above code into the following:

	q = READ_ONCE(a);
	WRITE_ONCE(b, 2);
	do_something_else();

Given this transformation, the CPU is not required to respect the ordering
between the load from variable 'a' and the store to variable 'b'.  It is
tempting to add a barrier(), but this does not help.  The conditional
is gone, and the barrier won't bring it back.  Therefore, if you are
relying on this ordering, you should make sure that MAX is greater than
one, perhaps as follows:

	q = READ_ONCE(a);
	BUILD_BUG_ON(MAX <= 1); /* Order load from a with store to b. */
	if (q % MAX) {
		WRITE_ONCE(b, 1);
		do_something();
	} else {
		WRITE_ONCE(b, 2);
		do_something_else();
	}

Please note once again that the stores to 'b' differ.  If they were
identical, as noted earlier, the compiler could pull this store outside
of the 'if' statement.

You must also be careful not to rely too much on boolean short-circuit
evaluation.  Consider this example:

	q = READ_ONCE(a);
	if (q || 1 > 0)
		WRITE_ONCE(b, 1);

Because the first condition cannot fault and the second condition is
always true, the compiler can transform this example as following,
defeating control dependency:

	q = READ_ONCE(a);
	WRITE_ONCE(b, 1);

This example underscores the need to ensure that the compiler cannot
out-guess your code.  More generally, although READ_ONCE() does force
the compiler to actually emit code for a given load, it does not force
the compiler to use the results.

In addition, control dependencies apply only to the then-clause and
else-clause of the if-statement in question.  In particular, it does
not necessarily apply to code following the if-statement:

	q = READ_ONCE(a);
	if (q) {
		WRITE_ONCE(b, 1);
	} else {
		WRITE_ONCE(b, 2);
	}
	WRITE_ONCE(c, 1);  /* BUG: No ordering against the read from 'a'. */

It is tempting to argue that there in fact is ordering because the
compiler cannot reorder volatile accesses and also cannot reorder
the writes to 'b' with the condition.  Unfortunately for this line
of reasoning, the compiler might compile the two writes to 'b' as
conditional-move instructions, as in this fanciful pseudo-assembly
language:

	ld r1,a
	cmp r1,$0
	cmov,ne r4,$1
	cmov,eq r4,$2
	st r4,b
	st $1,c

A weakly ordered CPU would have no dependency of any sort between the load
from 'a' and the store to 'c'.  The control dependencies would extend
only to the pair of cmov instructions and the store depending on them.
In short, control dependencies apply only to the stores in the then-clause
and else-clause of the if-statement in question (including functions
invoked by those two clauses), not to code following that if-statement.

Finally, control dependencies do -not- provide transitivity.  This is
demonstrated by two related examples, with the initial values of
'x' and 'y' both being zero:

	CPU 0                     CPU 1
	=======================   =======================
	r1 = READ_ONCE(x);        r2 = READ_ONCE(y);
	if (r1 > 0)               if (r2 > 0)
	  WRITE_ONCE(y, 1);         WRITE_ONCE(x, 1);

	assert(!(r1 == 1 && r2 == 1));

The above two-CPU example will never trigger the assert().  However,
if control dependencies guaranteed transitivity (which they do not),
then adding the following CPU would guarantee a related assertion:

	CPU 2
	=====================
	WRITE_ONCE(x, 2);

	assert(!(r1 == 2 && r2 == 1 && x == 2)); /* FAILS!!! */

But because control dependencies do -not- provide transitivity, the above
assertion can fail after the combined three-CPU example completes.  If you
need the three-CPU example to provide ordering, you will need smp_mb()
between the loads and stores in the CPU 0 and CPU 1 code fragments,
that is, just before or just after the "if" statements.  Furthermore,
the original two-CPU example is very fragile and should be avoided.

These two examples are the LB and WWC litmus tests from this paper:
http://www.cl.cam.ac.uk/users/pes20/ppc-supplemental/test6.pdf and this
site: https://www.cl.cam.ac.uk/~pes20/ppcmem/index.html.

In summary:

  (*) Control dependencies can order prior loads against later stores.
      However, they do -not- guarantee any other sort of ordering:
      Not prior loads against later loads, nor prior stores against
      later anything.  If you need these other forms of ordering,
      use smp_rmb(), smp_wmb(), or, in the case of prior stores and
      later loads, smp_mb().

  (*) If both legs of the "if" statement begin with identical stores to
      the same variable, then those stores must be ordered, either by
      preceding both of them with smp_mb() or by using smp_store_release()
      to carry out the stores.  Please note that it is -not- sufficient
      to use barrier() at beginning of each leg of the "if" statement
      because, as shown by the example above, optimizing compilers can
      destroy the control dependency while respecting the letter of the
      barrier() law.

  (*) Control dependencies require at least one run-time conditional
      between the prior load and the subsequent store, and this
      conditional must involve the prior load.  If the compiler is able
      to optimize the conditional away, it will have also optimized
      away the ordering.  Careful use of READ_ONCE() and WRITE_ONCE()
      can help to preserve the needed conditional.

  (*) Control dependencies require that the compiler avoid reordering the
      dependency into nonexistence.  Careful use of READ_ONCE() or
      atomic{,64}_read() can help to preserve your control dependency.
      Please see the COMPILER BARRIER section for more information.

  (*) Control dependencies apply only to the then-clause and else-clause
      of the if-statement containing the control dependency, including
      any functions that these two clauses call.  Control dependencies
      do -not- apply to code following the if-statement containing the
      control dependency.

  (*) Control dependencies pair normally with other types of barriers.

  (*) Control dependencies do -not- provide transitivity.  If you
      need transitivity, use smp_mb().

  (*) Compilers do not understand control dependencies.  It is therefore
      your job to ensure that they do not break your code.


SMP BARRIER PAIRING
-------------------

When dealing with CPU-CPU interactions, certain types of memory barrier should
always be paired.  A lack of appropriate pairing is almost certainly an error.

General barriers pair with each other, though they also pair with most
other types of barriers, albeit without transitivity.  An acquire barrier
pairs with a release barrier, but both may also pair with other barriers,
including of course general barriers.  A write barrier pairs with a data
dependency barrier, a control dependency, an acquire barrier, a release
barrier, a read barrier, or a general barrier.  Similarly a read barrier,
control dependency, or a data dependency barrier pairs with a write
barrier, an acquire barrier, a release barrier, or a general barrier:

	CPU 1		      CPU 2
	===============	      ===============
	WRITE_ONCE(a, 1);
	<write barrier>
	WRITE_ONCE(b, 2);     x = READ_ONCE(b);
			      <read barrier>
			      y = READ_ONCE(a);

Or:

	CPU 1		      CPU 2
	===============	      ===============================
	a = 1;
	<write barrier>
	WRITE_ONCE(b, &a);    x = READ_ONCE(b);
			      <data dependency barrier>
			      y = *x;

Or even:

	CPU 1		      CPU 2
	===============	      ===============================
	r1 = READ_ONCE(y);
	<general barrier>
	WRITE_ONCE(y, 1);     if (r2 = READ_ONCE(x)) {
			         <implicit control dependency>
			         WRITE_ONCE(y, 1);
			      }

	assert(r1 == 0 || r2 == 0);

Basically, the read barrier always has to be there, even though it can be of
the "weaker" type.

[!] Note that the stores before the write barrier would normally be expected to
match the loads after the read barrier or the data dependency barrier, and vice
versa:

	CPU 1                               CPU 2
	===================                 ===================
	WRITE_ONCE(a, 1);    }----   --->{  v = READ_ONCE(c);
	WRITE_ONCE(b, 2);    }    \ /    {  w = READ_ONCE(d);
	<write barrier>            \        <read barrier>
	WRITE_ONCE(c, 3);    }    / \    {  x = READ_ONCE(a);
	WRITE_ONCE(d, 4);    }----   --->{  y = READ_ONCE(b);


EXAMPLES OF MEMORY BARRIER SEQUENCES
------------------------------------

Firstly, write barriers act as partial orderings on store operations.
Consider the following sequence of events:

	CPU 1
	=======================
	STORE A = 1
	STORE B = 2
	STORE C = 3
	<write barrier>
	STORE D = 4
	STORE E = 5

This sequence of events is committed to the memory coherence system in an order
that the rest of the system might perceive as the unordered set of { STORE A,
STORE B, STORE C } all occurring before the unordered set of { STORE D, STORE E
}:

	+-------+       :      :
	|       |       +------+
	|       |------>| C=3  |     }     /\
	|       |  :    +------+     }-----  \  -----> Events perceptible to
	|       |  :    | A=1  |     }        \/       the rest of the system
	|       |  :    +------+     }
	| CPU 1 |  :    | B=2  |     }
	|       |       +------+     }
	|       |   wwwwwwwwwwwwwwww }   <--- At this point the write barrier
	|       |       +------+     }        requires all stores prior to the
	|       |  :    | E=5  |     }        barrier to be committed before
	|       |  :    +------+     }        further stores may take place
	|       |------>| D=4  |     }
	|       |       +------+
	+-------+       :      :
	                   |
	                   | Sequence in which stores are committed to the
	                   | memory system by CPU 1
	                   V


Secondly, data dependency barriers act as partial orderings on data-dependent
loads.  Consider the following sequence of events:

	CPU 1			CPU 2
	=======================	=======================
		{ B = 7; X = 9; Y = 8; C = &Y }
	STORE A = 1
	STORE B = 2
	<write barrier>
	STORE C = &B		LOAD X
	STORE D = 4		LOAD C (gets &B)
				LOAD *C (reads B)

Without intervention, CPU 2 may perceive the events on CPU 1 in some
effectively random order, despite the write barrier issued by CPU 1:

	+-------+       :      :                :       :
	|       |       +------+                +-------+  | Sequence of update
	|       |------>| B=2  |-----       --->| Y->8  |  | of perception on
	|       |  :    +------+     \          +-------+  | CPU 2
	| CPU 1 |  :    | A=1  |      \     --->| C->&Y |  V
	|       |       +------+       |        +-------+
	|       |   wwwwwwwwwwwwwwww   |        :       :
	|       |       +------+       |        :       :
	|       |  :    | C=&B |---    |        :       :       +-------+
	|       |  :    +------+   \   |        +-------+       |       |
	|       |------>| D=4  |    ----------->| C->&B |------>|       |
	|       |       +------+       |        +-------+       |       |
	+-------+       :      :       |        :       :       |       |
	                               |        :       :       |       |
	                               |        :       :       | CPU 2 |
	                               |        +-------+       |       |
	    Apparently incorrect --->  |        | B->7  |------>|       |
	    perception of B (!)        |        +-------+       |       |
	                               |        :       :       |       |
	                               |        +-------+       |       |
	    The load of X holds --->    \       | X->9  |------>|       |
	    up the maintenance           \      +-------+       |       |
	    of coherence of B             ----->| B->2  |       +-------+
	                                        +-------+
	                                        :       :


In the above example, CPU 2 perceives that B is 7, despite the load of *C
(which would be B) coming after the LOAD of C.

If, however, a data dependency barrier were to be placed between the load of C
and the load of *C (ie: B) on CPU 2:

	CPU 1			CPU 2
	=======================	=======================
		{ B = 7; X = 9; Y = 8; C = &Y }
	STORE A = 1
	STORE B = 2
	<write barrier>
	STORE C = &B		LOAD X
	STORE D = 4		LOAD C (gets &B)
				<data dependency barrier>
				LOAD *C (reads B)

then the following will occur:

	+-------+       :      :                :       :
	|       |       +------+                +-------+
	|       |------>| B=2  |-----       --->| Y->8  |
	|       |  :    +------+     \          +-------+
	| CPU 1 |  :    | A=1  |      \     --->| C->&Y |
	|       |       +------+       |        +-------+
	|       |   wwwwwwwwwwwwwwww   |        :       :
	|       |       +------+       |        :       :
	|       |  :    | C=&B |---    |        :       :       +-------+
	|       |  :    +------+   \   |        +-------+       |       |
	|       |------>| D=4  |    ----------->| C->&B |------>|       |
	|       |       +------+       |        +-------+       |       |
	+-------+       :      :       |        :       :       |       |
	                               |        :       :       |       |
	                               |        :       :       | CPU 2 |
	                               |        +-------+       |       |
	                               |        | X->9  |------>|       |
	                               |        +-------+       |       |
	  Makes sure all effects --->   \   ddddddddddddddddd   |       |
	  prior to the store of C        \      +-------+       |       |
	  are perceptible to              ----->| B->2  |------>|       |
	  subsequent loads                      +-------+       |       |
	                                        :       :       +-------+


And thirdly, a read barrier acts as a partial order on loads.  Consider the
following sequence of events:

	CPU 1			CPU 2
	=======================	=======================
		{ A = 0, B = 9 }
	STORE A=1
	<write barrier>
	STORE B=2
				LOAD B
				LOAD A

Without intervention, CPU 2 may then choose to perceive the events on CPU 1 in
some effectively random order, despite the write barrier issued by CPU 1:

	+-------+       :      :                :       :
	|       |       +------+                +-------+
	|       |------>| A=1  |------      --->| A->0  |
	|       |       +------+      \         +-------+
	| CPU 1 |   wwwwwwwwwwwwwwww   \    --->| B->9  |
	|       |       +------+        |       +-------+
	|       |------>| B=2  |---     |       :       :
	|       |       +------+   \    |       :       :       +-------+
	+-------+       :      :    \   |       +-------+       |       |
	                             ---------->| B->2  |------>|       |
	                                |       +-------+       | CPU 2 |
	                                |       | A->0  |------>|       |
	                                |       +-------+       |       |
	                                |       :       :       +-------+
	                                 \      :       :
	                                  \     +-------+
	                                   ---->| A->1  |
	                                        +-------+
	                                        :       :


If, however, a read barrier were to be placed between the load of B and the
load of A on CPU 2:

	CPU 1			CPU 2
	=======================	=======================
		{ A = 0, B = 9 }
	STORE A=1
	<write barrier>
	STORE B=2
				LOAD B
				<read barrier>
				LOAD A

then the partial ordering imposed by CPU 1 will be perceived correctly by CPU
2:

	+-------+       :      :                :       :
	|       |       +------+                +-------+
	|       |------>| A=1  |------      --->| A->0  |
	|       |       +------+      \         +-------+
	| CPU 1 |   wwwwwwwwwwwwwwww   \    --->| B->9  |
	|       |       +------+        |       +-------+
	|       |------>| B=2  |---     |       :       :
	|       |       +------+   \    |       :       :       +-------+
	+-------+       :      :    \   |       +-------+       |       |
	                             ---------->| B->2  |------>|       |
	                                |       +-------+       | CPU 2 |
	                                |       :       :       |       |
	                                |       :       :       |       |
	  At this point the read ---->   \  rrrrrrrrrrrrrrrrr   |       |
	  barrier causes all effects      \     +-------+       |       |
	  prior to the storage of B        ---->| A->1  |------>|       |
	  to be perceptible to CPU 2            +-------+       |       |
	                                        :       :       +-------+


To illustrate this more completely, consider what could happen if the code
contained a load of A either side of the read barrier:

	CPU 1			CPU 2
	=======================	=======================
		{ A = 0, B = 9 }
	STORE A=1
	<write barrier>
	STORE B=2
				LOAD B
				LOAD A [first load of A]
				<read barrier>
				LOAD A [second load of A]

Even though the two loads of A both occur after the load of B, they may both
come up with different values:

	+-------+       :      :                :       :
	|       |       +------+                +-------+
	|       |------>| A=1  |------      --->| A->0  |
	|       |       +------+      \         +-------+
	| CPU 1 |   wwwwwwwwwwwwwwww   \    --->| B->9  |
	|       |       +------+        |       +-------+
	|       |------>| B=2  |---     |       :       :
	|       |       +------+   \    |       :       :       +-------+
	+-------+       :      :    \   |       +-------+       |       |
	                             ---------->| B->2  |------>|       |
	                                |       +-------+       | CPU 2 |
	                                |       :       :       |       |
	                                |       :       :       |       |
	                                |       +-------+       |       |
	                                |       | A->0  |------>| 1st   |
	                                |       +-------+       |       |
	  At this point the read ---->   \  rrrrrrrrrrrrrrrrr   |       |
	  barrier causes all effects      \     +-------+       |       |
	  prior to the storage of B        ---->| A->1  |------>| 2nd   |
	  to be perceptible to CPU 2            +-------+       |       |
	                                        :       :       +-------+


But it may be that the update to A from CPU 1 becomes perceptible to CPU 2
before the read barrier completes anyway:

	+-------+       :      :                :       :
	|       |       +------+                +-------+
	|       |------>| A=1  |------      --->| A->0  |
	|       |       +------+      \         +-------+
	| CPU 1 |   wwwwwwwwwwwwwwww   \    --->| B->9  |
	|       |       +------+        |       +-------+
	|       |------>| B=2  |---     |       :       :
	|       |       +------+   \    |       :       :       +-------+
	+-------+       :      :    \   |       +-------+       |       |
	                             ---------->| B->2  |------>|       |
	                                |       +-------+       | CPU 2 |
	                                |       :       :       |       |
	                                 \      :       :       |       |
	                                  \     +-------+       |       |
	                                   ---->| A->1  |------>| 1st   |
	                                        +-------+       |       |
	                                    rrrrrrrrrrrrrrrrr   |       |
	                                        +-------+       |       |
	                                        | A->1  |------>| 2nd   |
	                                        +-------+       |       |
	                                        :       :       +-------+


The guarantee is that the second load will always come up with A == 1 if the
load of B came up with B == 2.  No such guarantee exists for the first load of
A; that may come up with either A == 0 or A == 1.


READ MEMORY BARRIERS VS LOAD SPECULATION
----------------------------------------

Many CPUs speculate with loads: that is they see that they will need to load an
item from memory, and they find a time where they're not using the bus for any
other loads, and so do the load in advance - even though they haven't actually
got to that point in the instruction execution flow yet.  This permits the
actual load instruction to potentially complete immediately because the CPU
already has the value to hand.

It may turn out that the CPU didn't actually need the value - perhaps because a
branch circumvented the load - in which case it can discard the value or just
cache it for later use.

Consider:

	CPU 1			CPU 2
	=======================	=======================
				LOAD B
				DIVIDE		} Divide instructions generally
				DIVIDE		} take a long time to perform
				LOAD A

Which might appear as this:

	                                        :       :       +-------+
	                                        +-------+       |       |
	                                    --->| B->2  |------>|       |
	                                        +-------+       | CPU 2 |
	                                        :       :DIVIDE |       |
	                                        +-------+       |       |
	The CPU being busy doing a --->     --->| A->0  |~~~~   |       |
	division speculates on the              +-------+   ~   |       |
	LOAD of A                               :       :   ~   |       |
	                                        :       :DIVIDE |       |
	                                        :       :   ~   |       |
	Once the divisions are complete -->     :       :   ~-->|       |
	the CPU can then perform the            :       :       |       |
	LOAD with immediate effect              :       :       +-------+


Placing a read barrier or a data dependency barrier just before the second
load:

	CPU 1			CPU 2
	=======================	=======================
				LOAD B
				DIVIDE
				DIVIDE
				<read barrier>
				LOAD A

will force any value speculatively obtained to be reconsidered to an extent
dependent on the type of barrier used.  If there was no change made to the
speculated memory location, then the speculated value will just be used:

	                                        :       :       +-------+
	                                        +-------+       |       |
	                                    --->| B->2  |------>|       |
	                                        +-------+       | CPU 2 |
	                                        :       :DIVIDE |       |
	                                        +-------+       |       |
	The CPU being busy doing a --->     --->| A->0  |~~~~   |       |
	division speculates on the              +-------+   ~   |       |
	LOAD of A                               :       :   ~   |       |
	                                        :       :DIVIDE |       |
	                                        :       :   ~   |       |
	                                        :       :   ~   |       |
	                                    rrrrrrrrrrrrrrrr~   |       |
	                                        :       :   ~   |       |
	                                        :       :   ~-->|       |
	                                        :       :       |       |
	                                        :       :       +-------+


but if there was an update or an invalidation from another CPU pending, then
the speculation will be cancelled and the value reloaded:

	                                        :       :       +-------+
	                                        +-------+       |       |
	                                    --->| B->2  |------>|       |
	                                        +-------+       | CPU 2 |
	                                        :       :DIVIDE |       |
	                                        +-------+       |       |
	The CPU being busy doing a --->     --->| A->0  |~~~~   |       |
	division speculates on the              +-------+   ~   |       |
	LOAD of A                               :       :   ~   |       |
	                                        :       :DIVIDE |       |
	                                        :       :   ~   |       |
	                                        :       :   ~   |       |
	                                    rrrrrrrrrrrrrrrrr   |       |
	                                        +-------+       |       |
	The speculation is discarded --->   --->| A->1  |------>|       |
	and an updated value is                 +-------+       |       |
	retrieved                               :       :       +-------+


TRANSITIVITY
------------

Transitivity is a deeply intuitive notion about ordering that is not
always provided by real computer systems.  The following example
demonstrates transitivity:

	CPU 1			CPU 2			CPU 3
	=======================	=======================	=======================
		{ X = 0, Y = 0 }
	STORE X=1		LOAD X			STORE Y=1
				<general barrier>	<general barrier>
				LOAD Y			LOAD X

Suppose that CPU 2's load from X returns 1 and its load from Y returns 0.
This indicates that CPU 2's load from X in some sense follows CPU 1's
store to X and that CPU 2's load from Y in some sense preceded CPU 3's
store to Y.  The question is then "Can CPU 3's load from X return 0?"

Because CPU 2's load from X in some sense came after CPU 1's store, it
is natural to expect that CPU 3's load from X must therefore return 1.
This expectation is an example of transitivity: if a load executing on
CPU A follows a load from the same variable executing on CPU B, then
CPU A's load must either return the same value that CPU B's load did,
or must return some later value.

In the Linux kernel, use of general memory barriers guarantees
transitivity.  Therefore, in the above example, if CPU 2's load from X
returns 1 and its load from Y returns 0, then CPU 3's load from X must
also return 1.

However, transitivity is -not- guaranteed for read or write barriers.
For example, suppose that CPU 2's general barrier in the above example
is changed to a read barrier as shown below:

	CPU 1			CPU 2			CPU 3
	=======================	=======================	=======================
		{ X = 0, Y = 0 }
	STORE X=1		LOAD X			STORE Y=1
				<read barrier>		<general barrier>
				LOAD Y			LOAD X

This substitution destroys transitivity: in this example, it is perfectly
legal for CPU 2's load from X to return 1, its load from Y to return 0,
and CPU 3's load from X to return 0.

The key point is that although CPU 2's read barrier orders its pair
of loads, it does not guarantee to order CPU 1's store.  Therefore, if
this example runs on a system where CPUs 1 and 2 share a store buffer
or a level of cache, CPU 2 might have early access to CPU 1's writes.
General barriers are therefore required to ensure that all CPUs agree
on the combined order of CPU 1's and CPU 2's accesses.

General barriers provide "global transitivity", so that all CPUs will
agree on the order of operations.  In contrast, a chain of release-acquire
pairs provides only "local transitivity", so that only those CPUs on
the chain are guaranteed to agree on the combined order of the accesses.
For example, switching to C code in deference to Herman Hollerith:

	int u, v, x, y, z;

	void cpu0(void)
	{
		r0 = smp_load_acquire(&x);
		WRITE_ONCE(u, 1);
		smp_store_release(&y, 1);
	}

	void cpu1(void)
	{
		r1 = smp_load_acquire(&y);
		r4 = READ_ONCE(v);
		r5 = READ_ONCE(u);
		smp_store_release(&z, 1);
	}

	void cpu2(void)
	{
		r2 = smp_load_acquire(&z);
		smp_store_release(&x, 1);
	}

	void cpu3(void)
	{
		WRITE_ONCE(v, 1);
		smp_mb();
		r3 = READ_ONCE(u);
	}

Because cpu0(), cpu1(), and cpu2() participate in a local transitive
chain of smp_store_release()/smp_load_acquire() pairs, the following
outcome is prohibited:

	r0 == 1 && r1 == 1 && r2 == 1

Furthermore, because of the release-acquire relationship between cpu0()
and cpu1(), cpu1() must see cpu0()'s writes, so that the following
outcome is prohibited:

	r1 == 1 && r5 == 0

However, the transitivity of release-acquire is local to the participating
CPUs and does not apply to cpu3().  Therefore, the following outcome
is possible:

	r0 == 0 && r1 == 1 && r2 == 1 && r3 == 0 && r4 == 0

As an aside, the following outcome is also possible:

	r0 == 0 && r1 == 1 && r2 == 1 && r3 == 0 && r4 == 0 && r5 == 1

Although cpu0(), cpu1(), and cpu2() will see their respective reads and
writes in order, CPUs not involved in the release-acquire chain might
well disagree on the order.  This disagreement stems from the fact that
the weak memory-barrier instructions used to implement smp_load_acquire()
and smp_store_release() are not required to order prior stores against
subsequent loads in all cases.  This means that cpu3() can see cpu0()'s
store to u as happening -after- cpu1()'s load from v, even though
both cpu0() and cpu1() agree that these two operations occurred in the
intended order.

However, please keep in mind that smp_load_acquire() is not magic.
In particular, it simply reads from its argument with ordering.  It does
-not- ensure that any particular value will be read.  Therefore, the
following outcome is possible:

	r0 == 0 && r1 == 0 && r2 == 0 && r5 == 0

Note that this outcome can happen even on a mythical sequentially
consistent system where nothing is ever reordered.

To reiterate, if your code requires global transitivity, use general
barriers throughout.


========================
EXPLICIT KERNEL BARRIERS
========================

The Linux kernel has a variety of different barriers that act at different
levels:

  (*) Compiler barrier.

  (*) CPU memory barriers.

  (*) MMIO write barrier.


COMPILER BARRIER
----------------

The Linux kernel has an explicit compiler barrier function that prevents the
compiler from moving the memory accesses either side of it to the other side:

	barrier();

This is a general barrier -- there are no read-read or write-write
variants of barrier().  However, READ_ONCE() and WRITE_ONCE() can be
thought of as weak forms of barrier() that affect only the specific
accesses flagged by the READ_ONCE() or WRITE_ONCE().

The barrier() function has the following effects:

 (*) Prevents the compiler from reordering accesses following the
     barrier() to precede any accesses preceding the barrier().
     One example use for this property is to ease communication between
     interrupt-handler code and the code that was interrupted.

 (*) Within a loop, forces the compiler to load the variables used
     in that loop's conditional on each pass through that loop.

The READ_ONCE() and WRITE_ONCE() functions can prevent any number of
optimizations that, while perfectly safe in single-threaded code, can
be fatal in concurrent code.  Here are some examples of these sorts
of optimizations:

 (*) The compiler is within its rights to reorder loads and stores
     to the same variable, and in some cases, the CPU is within its
     rights to reorder loads to the same variable.  This means that
     the following code:

	a[0] = x;
	a[1] = x;

     Might result in an older value of x stored in a[1] than in a[0].
     Prevent both the compiler and the CPU from doing this as follows:

	a[0] = READ_ONCE(x);
	a[1] = READ_ONCE(x);

     In short, READ_ONCE() and WRITE_ONCE() provide cache coherence for
     accesses from multiple CPUs to a single variable.

 (*) The compiler is within its rights to merge successive loads from
     the same variable.  Such merging can cause the compiler to "optimize"
     the following code:

	while (tmp = a)
		do_something_with(tmp);

     into the following code, which, although in some sense legitimate
     for single-threaded code, is almost certainly not what the developer
     intended:

	if (tmp = a)
		for (;;)
			do_something_with(tmp);

     Use READ_ONCE() to prevent the compiler from doing this to you:

	while (tmp = READ_ONCE(a))
		do_something_with(tmp);

 (*) The compiler is within its rights to reload a variable, for example,
     in cases where high register pressure prevents the compiler from
     keeping all data of interest in registers.  The compiler might
     therefore optimize the variable 'tmp' out of our previous example:

	while (tmp = a)
		do_something_with(tmp);

     This could result in the following code, which is perfectly safe in
     single-threaded code, but can be fatal in concurrent code:

	while (a)
		do_something_with(a);

     For example, the optimized version of this code could result in
     passing a zero to do_something_with() in the case where the variable
     a was modified by some other CPU between the "while" statement and
     the call to do_something_with().

     Again, use READ_ONCE() to prevent the compiler from doing this:

	while (tmp = READ_ONCE(a))
		do_something_with(tmp);

     Note that if the compiler runs short of registers, it might save
     tmp onto the stack.  The overhead of this saving and later restoring
     is why compilers reload variables.  Doing so is perfectly safe for
     single-threaded code, so you need to tell the compiler about cases
     where it is not safe.

 (*) The compiler is within its rights to omit a load entirely if it knows
     what the value will be.  For example, if the compiler can prove that
     the value of variable 'a' is always zero, it can optimize this code:

	while (tmp = a)
		do_something_with(tmp);

     Into this:

	do { } while (0);

     This transformation is a win for single-threaded code because it
     gets rid of a load and a branch.  The problem is that the compiler
     will carry out its proof assuming that the current CPU is the only
     one updating variable 'a'.  If variable 'a' is shared, then the
     compiler's proof will be erroneous.  Use READ_ONCE() to tell the
     compiler that it doesn't know as much as it thinks it does:

	while (tmp = READ_ONCE(a))
		do_something_with(tmp);

     But please note that the compiler is also closely watching what you
     do with the value after the READ_ONCE().  For example, suppose you
     do the following and MAX is a preprocessor macro with the value 1:

	while ((tmp = READ_ONCE(a)) % MAX)
		do_something_with(tmp);

     Then the compiler knows that the result of the "%" operator applied
     to MAX will always be zero, again allowing the compiler to optimize
     the code into near-nonexistence.  (It will still load from the
     variable 'a'.)

 (*) Similarly, the compiler is within its rights to omit a store entirely
     if it knows that the variable already has the value being stored.
     Again, the compiler assumes that the current CPU is the only one
     storing into the variable, which can cause the compiler to do the
     wrong thing for shared variables.  For example, suppose you have
     the following:

	a = 0;
	... Code that does not store to variable a ...
	a = 0;

     The compiler sees that the value of variable 'a' is already zero, so
     it might well omit the second store.  This would come as a fatal
     surprise if some other CPU might have stored to variable 'a' in the
     meantime.

     Use WRITE_ONCE() to prevent the compiler from making this sort of
     wrong guess:

	WRITE_ONCE(a, 0);
	... Code that does not store to variable a ...
	WRITE_ONCE(a, 0);

 (*) The compiler is within its rights to reorder memory accesses unless
     you tell it not to.  For example, consider the following interaction
     between process-level code and an interrupt handler:

	void process_level(void)
	{
		msg = get_message();
		flag = true;
	}

	void interrupt_handler(void)
	{
		if (flag)
			process_message(msg);
	}

     There is nothing to prevent the compiler from transforming
     process_level() to the following, in fact, this might well be a
     win for single-threaded code:

	void process_level(void)
	{
		flag = true;
		msg = get_message();
	}

     If the interrupt occurs between these two statement, then
     interrupt_handler() might be passed a garbled msg.  Use WRITE_ONCE()
     to prevent this as follows:

	void process_level(void)
	{
		WRITE_ONCE(msg, get_message());
		WRITE_ONCE(flag, true);
	}

	void interrupt_handler(void)
	{
		if (READ_ONCE(flag))
			process_message(READ_ONCE(msg));
	}

     Note that the READ_ONCE() and WRITE_ONCE() wrappers in
     interrupt_handler() are needed if this interrupt handler can itself
     be interrupted by something that also accesses 'flag' and 'msg',
     for example, a nested interrupt or an NMI.  Otherwise, READ_ONCE()
     and WRITE_ONCE() are not needed in interrupt_handler() other than
     for documentation purposes.  (Note also that nested interrupts
     do not typically occur in modern Linux kernels, in fact, if an
     interrupt handler returns with interrupts enabled, you will get a
     WARN_ONCE() splat.)

     You should assume that the compiler can move READ_ONCE() and
     WRITE_ONCE() past code not containing READ_ONCE(), WRITE_ONCE(),
     barrier(), or similar primitives.

     This effect could also be achieved using barrier(), but READ_ONCE()
     and WRITE_ONCE() are more selective:  With READ_ONCE() and
     WRITE_ONCE(), the compiler need only forget the contents of the
     indicated memory locations, while with barrier() the compiler must
     discard the value of all memory locations that it has currented
     cached in any machine registers.  Of course, the compiler must also
     respect the order in which the READ_ONCE()s and WRITE_ONCE()s occur,
     though the CPU of course need not do so.

 (*) The compiler is within its rights to invent stores to a variable,
     as in the following example:

	if (a)
		b = a;
	else
		b = 42;

     The compiler might save a branch by optimizing this as follows:

	b = 42;
	if (a)
		b = a;

     In single-threaded code, this is not only safe, but also saves
     a branch.  Unfortunately, in concurrent code, this optimization
     could cause some other CPU to see a spurious value of 42 -- even
     if variable 'a' was never zero -- when loading variable 'b'.
     Use WRITE_ONCE() to prevent this as follows:

	if (a)
		WRITE_ONCE(b, a);
	else
		WRITE_ONCE(b, 42);

     The compiler can also invent loads.  These are usually less
     damaging, but they can result in cache-line bouncing and thus in
     poor performance and scalability.  Use READ_ONCE() to prevent
     invented loads.

 (*) For aligned memory locations whose size allows them to be accessed
     with a single memory-reference instruction, prevents "load tearing"
     and "store tearing," in which a single large access is replaced by
     multiple smaller accesses.  For example, given an architecture having
     16-bit store instructions with 7-bit immediate fields, the compiler
     might be tempted to use two 16-bit store-immediate instructions to
     implement the following 32-bit store:

	p = 0x00010002;

     Please note that GCC really does use this sort of optimization,
     which is not surprising given that it would likely take more
     than two instructions to build the constant and then store it.
     This optimization can therefore be a win in single-threaded code.
     In fact, a recent bug (since fixed) caused GCC to incorrectly use
     this optimization in a volatile store.  In the absence of such bugs,
     use of WRITE_ONCE() prevents store tearing in the following example:

	WRITE_ONCE(p, 0x00010002);

     Use of packed structures can also result in load and store tearing,
     as in this example:

	struct __attribute__((__packed__)) foo {
		short a;
		int b;
		short c;
	};
	struct foo foo1, foo2;
	...

	foo2.a = foo1.a;
	foo2.b = foo1.b;
	foo2.c = foo1.c;

     Because there are no READ_ONCE() or WRITE_ONCE() wrappers and no
     volatile markings, the compiler would be well within its rights to
     implement these three assignment statements as a pair of 32-bit
     loads followed by a pair of 32-bit stores.  This would result in
     load tearing on 'foo1.b' and store tearing on 'foo2.b'.  READ_ONCE()
     and WRITE_ONCE() again prevent tearing in this example:

	foo2.a = foo1.a;
	WRITE_ONCE(foo2.b, READ_ONCE(foo1.b));
	foo2.c = foo1.c;

All that aside, it is never necessary to use READ_ONCE() and
WRITE_ONCE() on a variable that has been marked volatile.  For example,
because 'jiffies' is marked volatile, it is never necessary to
say READ_ONCE(jiffies).  The reason for this is that READ_ONCE() and
WRITE_ONCE() are implemented as volatile casts, which has no effect when
its argument is already marked volatile.

Please note that these compiler barriers have no direct effect on the CPU,
which may then reorder things however it wishes.


CPU MEMORY BARRIERS
-------------------

The Linux kernel has eight basic CPU memory barriers:

	TYPE		MANDATORY		SMP CONDITIONAL
	===============	=======================	===========================
	GENERAL		mb()			smp_mb()
	WRITE		wmb()			smp_wmb()
	READ		rmb()			smp_rmb()
	DATA DEPENDENCY	read_barrier_depends()	smp_read_barrier_depends()


All memory barriers except the data dependency barriers imply a compiler
barrier.  Data dependencies do not impose any additional compiler ordering.

Aside: In the case of data dependencies, the compiler would be expected
to issue the loads in the correct order (eg. `a[b]` would have to load
the value of b before loading a[b]), however there is no guarantee in
the C specification that the compiler may not speculate the value of b
(eg. is equal to 1) and load a before b (eg. tmp = a[1]; if (b != 1)
tmp = a[b]; ).  There is also the problem of a compiler reloading b after
having loaded a[b], thus having a newer copy of b than a[b].  A consensus
has not yet been reached about these problems, however the READ_ONCE()
macro is a good place to start looking.

SMP memory barriers are reduced to compiler barriers on uniprocessor compiled
systems because it is assumed that a CPU will appear to be self-consistent,
and will order overlapping accesses correctly with respect to itself.
However, see the subsection on "Virtual Machine Guests" below.

[!] Note that SMP memory barriers _must_ be used to control the ordering of
references to shared memory on SMP systems, though the use of locking instead
is sufficient.

Mandatory barriers should not be used to control SMP effects, since mandatory
barriers impose unnecessary overhead on both SMP and UP systems. They may,
however, be used to control MMIO effects on accesses through relaxed memory I/O
windows.  These barriers are required even on non-SMP systems as they affect
the order in which memory operations appear to a device by prohibiting both the
compiler and the CPU from reordering them.


There are some more advanced barrier functions:

 (*) smp_store_mb(var, value)

     This assigns the value to the variable and then inserts a full memory
     barrier after it.  It isn't guaranteed to insert anything more than a
     compiler barrier in a UP compilation.


 (*) smp_mb__before_atomic();
 (*) smp_mb__after_atomic();

     These are for use with atomic (such as add, subtract, increment and
     decrement) functions that don't return a value, especially when used for
     reference counting.  These functions do not imply memory barriers.

     These are also used for atomic bitop functions that do not return a
     value (such as set_bit and clear_bit).

     As an example, consider a piece of code that marks an object as being dead
     and then decrements the object's reference count:

	obj->dead = 1;
	smp_mb__before_atomic();
	atomic_dec(&obj->ref_count);

     This makes sure that the death mark on the object is perceived to be set
     *before* the reference counter is decremented.

     See Documentation/atomic_{t,bitops}.txt for more information.


 (*) lockless_dereference();

     This can be thought of as a pointer-fetch wrapper around the
     smp_read_barrier_depends() data-dependency barrier.

     This is also similar to rcu_dereference(), but in cases where
     object lifetime is handled by some mechanism other than RCU, for
     example, when the objects removed only when the system goes down.
     In addition, lockless_dereference() is used in some data structures
     that can be used both with and without RCU.


 (*) dma_wmb();
 (*) dma_rmb();

     These are for use with consistent memory to guarantee the ordering
     of writes or reads of shared memory accessible to both the CPU and a
     DMA capable device.

     For example, consider a device driver that shares memory with a device
     and uses a descriptor status value to indicate if the descriptor belongs
     to the device or the CPU, and a doorbell to notify it when new
     descriptors are available:

	if (desc->status != DEVICE_OWN) {
		/* do not read data until we own descriptor */
		dma_rmb();

		/* read/modify data */
		read_data = desc->data;
		desc->data = write_data;

		/* flush modifications before status update */
		dma_wmb();

		/* assign ownership */
		desc->status = DEVICE_OWN;

		/* force memory to sync before notifying device via MMIO */
		wmb();

		/* notify device of new descriptors */
		writel(DESC_NOTIFY, doorbell);
	}

     The dma_rmb() allows us guarantee the device has released ownership
     before we read the data from the descriptor, and the dma_wmb() allows
     us to guarantee the data is written to the descriptor before the device
     can see it now has ownership.  The wmb() is needed to guarantee that the
     cache coherent memory writes have completed before attempting a write to
     the cache incoherent MMIO region.

     See Documentation/DMA-API.txt for more information on consistent memory.


MMIO WRITE BARRIER
------------------

The Linux kernel also has a special barrier for use with memory-mapped I/O
writes:

	mmiowb();

This is a variation on the mandatory write barrier that causes writes to weakly
ordered I/O regions to be partially ordered.  Its effects may go beyond the
CPU->Hardware interface and actually affect the hardware at some level.

See the subsection "Acquires vs I/O accesses" for more information.


===============================
IMPLICIT KERNEL MEMORY BARRIERS
===============================

Some of the other functions in the linux kernel imply memory barriers, amongst
which are locking and scheduling functions.

This specification is a _minimum_ guarantee; any particular architecture may
provide more substantial guarantees, but these may not be relied upon outside
of arch specific code.


LOCK ACQUISITION FUNCTIONS
--------------------------

The Linux kernel has a number of locking constructs:

 (*) spin locks
 (*) R/W spin locks
 (*) mutexes
 (*) semaphores
 (*) R/W semaphores

In all cases there are variants on "ACQUIRE" operations and "RELEASE" operations
for each construct.  These operations all imply certain barriers:

 (1) ACQUIRE operation implication:

     Memory operations issued after the ACQUIRE will be completed after the
     ACQUIRE operation has completed.

     Memory operations issued before the ACQUIRE may be completed after
     the ACQUIRE operation has completed.

 (2) RELEASE operation implication:

     Memory operations issued before the RELEASE will be completed before the
     RELEASE operation has completed.

     Memory operations issued after the RELEASE may be completed before the
     RELEASE operation has completed.

 (3) ACQUIRE vs ACQUIRE implication:

     All ACQUIRE operations issued before another ACQUIRE operation will be
     completed before that ACQUIRE operation.

 (4) ACQUIRE vs RELEASE implication:

     All ACQUIRE operations issued before a RELEASE operation will be
     completed before the RELEASE operation.

 (5) Failed conditional ACQUIRE implication:

     Certain locking variants of the ACQUIRE operation may fail, either due to
     being unable to get the lock immediately, or due to receiving an unblocked
     signal whilst asleep waiting for the lock to become available.  Failed
     locks do not imply any sort of barrier.

[!] Note: one of the consequences of lock ACQUIREs and RELEASEs being only
one-way barriers is that the effects of instructions outside of a critical
section may seep into the inside of the critical section.

An ACQUIRE followed by a RELEASE may not be assumed to be full memory barrier
because it is possible for an access preceding the ACQUIRE to happen after the
ACQUIRE, and an access following the RELEASE to happen before the RELEASE, and
the two accesses can themselves then cross:

	*A = a;
	ACQUIRE M
	RELEASE M
	*B = b;

may occur as:

	ACQUIRE M, STORE *B, STORE *A, RELEASE M

When the ACQUIRE and RELEASE are a lock acquisition and release,
respectively, this same reordering can occur if the lock's ACQUIRE and
RELEASE are to the same lock variable, but only from the perspective of
another CPU not holding that lock.  In short, a ACQUIRE followed by an
RELEASE may -not- be assumed to be a full memory barrier.

Similarly, the reverse case of a RELEASE followed by an ACQUIRE does
not imply a full memory barrier.  Therefore, the CPU's execution of the
critical sections corresponding to the RELEASE and the ACQUIRE can cross,
so that:

	*A = a;
	RELEASE M
	ACQUIRE N
	*B = b;

could occur as:

	ACQUIRE N, STORE *B, STORE *A, RELEASE M

It might appear that this reordering could introduce a deadlock.
However, this cannot happen because if such a deadlock threatened,
the RELEASE would simply complete, thereby avoiding the deadlock.

	Why does this work?

	One key point is that we are only talking about the CPU doing
	the reordering, not the compiler.  If the compiler (or, for
	that matter, the developer) switched the operations, deadlock
	-could- occur.

	But suppose the CPU reordered the operations.  In this case,
	the unlock precedes the lock in the assembly code.  The CPU
	simply elected to try executing the later lock operation first.
	If there is a deadlock, this lock operation will simply spin (or
	try to sleep, but more on that later).	The CPU will eventually
	execute the unlock operation (which preceded the lock operation
	in the assembly code), which will unravel the potential deadlock,
	allowing the lock operation to succeed.

	But what if the lock is a sleeplock?  In that case, the code will
	try to enter the scheduler, where it will eventually encounter
	a memory barrier, which will force the earlier unlock operation
	to complete, again unraveling the deadlock.  There might be
	a sleep-unlock race, but the locking primitive needs to resolve
	such races properly in any case.

Locks and semaphores may not provide any guarantee of ordering on UP compiled
systems, and so cannot be counted on in such a situation to actually achieve
anything at all - especially with respect to I/O accesses - unless combined
with interrupt disabling operations.

See also the section on "Inter-CPU acquiring barrier effects".


As an example, consider the following:

	*A = a;
	*B = b;
	ACQUIRE
	*C = c;
	*D = d;
	RELEASE
	*E = e;
	*F = f;

The following sequence of events is acceptable:

	ACQUIRE, {*F,*A}, *E, {*C,*D}, *B, RELEASE

	[+] Note that {*F,*A} indicates a combined access.

But none of the following are:

	{*F,*A}, *B,	ACQUIRE, *C, *D,	RELEASE, *E
	*A, *B, *C,	ACQUIRE, *D,		RELEASE, *E, *F
	*A, *B,		ACQUIRE, *C,		RELEASE, *D, *E, *F
	*B,		ACQUIRE, *C, *D,	RELEASE, {*F,*A}, *E



INTERRUPT DISABLING FUNCTIONS
-----------------------------

Functions that disable interrupts (ACQUIRE equivalent) and enable interrupts
(RELEASE equivalent) will act as compiler barriers only.  So if memory or I/O
barriers are required in such a situation, they must be provided from some
other means.


SLEEP AND WAKE-UP FUNCTIONS
---------------------------

Sleeping and waking on an event flagged in global data can be viewed as an
interaction between two pieces of data: the task state of the task waiting for
the event and the global data used to indicate the event.  To make sure that
these appear to happen in the right order, the primitives to begin the process
of going to sleep, and the primitives to initiate a wake up imply certain
barriers.

Firstly, the sleeper normally follows something like this sequence of events:

	for (;;) {
		set_current_state(TASK_UNINTERRUPTIBLE);
		if (event_indicated)
			break;
		schedule();
	}

A general memory barrier is interpolated automatically by set_current_state()
after it has altered the task state:

	CPU 1
	===============================
	set_current_state();
	  smp_store_mb();
	    STORE current->state
	    <general barrier>
	LOAD event_indicated

set_current_state() may be wrapped by:

	prepare_to_wait();
	prepare_to_wait_exclusive();

which therefore also imply a general memory barrier after setting the state.
The whole sequence above is available in various canned forms, all of which
interpolate the memory barrier in the right place:

	wait_event();
	wait_event_interruptible();
	wait_event_interruptible_exclusive();
	wait_event_interruptible_timeout();
	wait_event_killable();
	wait_event_timeout();
	wait_on_bit();
	wait_on_bit_lock();


Secondly, code that performs a wake up normally follows something like this:

	event_indicated = 1;
	wake_up(&event_wait_queue);

or:

	event_indicated = 1;
	wake_up_process(event_daemon);

A write memory barrier is implied by wake_up() and co.  if and only if they
wake something up.  The barrier occurs before the task state is cleared, and so
sits between the STORE to indicate the event and the STORE to set TASK_RUNNING:

	CPU 1				CPU 2
	===============================	===============================
	set_current_state();		STORE event_indicated
	  smp_store_mb();		wake_up();
	    STORE current->state	  <write barrier>
	    <general barrier>		  STORE current->state
	LOAD event_indicated

To repeat, this write memory barrier is present if and only if something
is actually awakened.  To see this, consider the following sequence of
events, where X and Y are both initially zero:

	CPU 1				CPU 2
	===============================	===============================
	X = 1;				STORE event_indicated
	smp_mb();			wake_up();
	Y = 1;				wait_event(wq, Y == 1);
	wake_up();			  load from Y sees 1, no memory barrier
					load from X might see 0

In contrast, if a wakeup does occur, CPU 2's load from X would be guaranteed
to see 1.

The available waker functions include:

	complete();
	wake_up();
	wake_up_all();
	wake_up_bit();
	wake_up_interruptible();
	wake_up_interruptible_all();
	wake_up_interruptible_nr();
	wake_up_interruptible_poll();
	wake_up_interruptible_sync();
	wake_up_interruptible_sync_poll();
	wake_up_locked();
	wake_up_locked_poll();
	wake_up_nr();
	wake_up_poll();
	wake_up_process();


[!] Note that the memory barriers implied by the sleeper and the waker do _not_
order multiple stores before the wake-up with respect to loads of those stored
values after the sleeper has called set_current_state().  For instance, if the
sleeper does:

	set_current_state(TASK_INTERRUPTIBLE);
	if (event_indicated)
		break;
	__set_current_state(TASK_RUNNING);
	do_something(my_data);

and the waker does:

	my_data = value;
	event_indicated = 1;
	wake_up(&event_wait_queue);

there's no guarantee that the change to event_indicated will be perceived by
the sleeper as coming after the change to my_data.  In such a circumstance, the
code on both sides must interpolate its own memory barriers between the
separate data accesses.  Thus the above sleeper ought to do:

	set_current_state(TASK_INTERRUPTIBLE);
	if (event_indicated) {
		smp_rmb();
		do_something(my_data);
	}

and the waker should do:

	my_data = value;
	smp_wmb();
	event_indicated = 1;
	wake_up(&event_wait_queue);


MISCELLANEOUS FUNCTIONS
-----------------------

Other functions that imply barriers:

 (*) schedule() and similar imply full memory barriers.


===================================
INTER-CPU ACQUIRING BARRIER EFFECTS
===================================

On SMP systems locking primitives give a more substantial form of barrier: one
that does affect memory access ordering on other CPUs, within the context of
conflict on any particular lock.


ACQUIRES VS MEMORY ACCESSES
---------------------------

Consider the following: the system has a pair of spinlocks (M) and (Q), and
three CPUs; then should the following sequence of events occur:

	CPU 1				CPU 2
	===============================	===============================
	WRITE_ONCE(*A, a);		WRITE_ONCE(*E, e);
	ACQUIRE M			ACQUIRE Q
	WRITE_ONCE(*B, b);		WRITE_ONCE(*F, f);
	WRITE_ONCE(*C, c);		WRITE_ONCE(*G, g);
	RELEASE M			RELEASE Q
	WRITE_ONCE(*D, d);		WRITE_ONCE(*H, h);

Then there is no guarantee as to what order CPU 3 will see the accesses to *A
through *H occur in, other than the constraints imposed by the separate locks
on the separate CPUs.  It might, for example, see:

	*E, ACQUIRE M, ACQUIRE Q, *G, *C, *F, *A, *B, RELEASE Q, *D, *H, RELEASE M

But it won't see any of:

	*B, *C or *D preceding ACQUIRE M
	*A, *B or *C following RELEASE M
	*F, *G or *H preceding ACQUIRE Q
	*E, *F or *G following RELEASE Q



ACQUIRES VS I/O ACCESSES
------------------------

Under certain circumstances (especially involving NUMA), I/O accesses within
two spinlocked sections on two different CPUs may be seen as interleaved by the
PCI bridge, because the PCI bridge does not necessarily participate in the
cache-coherence protocol, and is therefore incapable of issuing the required
read memory barriers.

For example:

	CPU 1				CPU 2
	===============================	===============================
	spin_lock(Q)
	writel(0, ADDR)
	writel(1, DATA);
	spin_unlock(Q);
					spin_lock(Q);
					writel(4, ADDR);
					writel(5, DATA);
					spin_unlock(Q);

may be seen by the PCI bridge as follows:

	STORE *ADDR = 0, STORE *ADDR = 4, STORE *DATA = 1, STORE *DATA = 5

which would probably cause the hardware to malfunction.


What is necessary here is to intervene with an mmiowb() before dropping the
spinlock, for example:

	CPU 1				CPU 2
	===============================	===============================
	spin_lock(Q)
	writel(0, ADDR)
	writel(1, DATA);
	mmiowb();
	spin_unlock(Q);
					spin_lock(Q);
					writel(4, ADDR);
					writel(5, DATA);
					mmiowb();
					spin_unlock(Q);

this will ensure that the two stores issued on CPU 1 appear at the PCI bridge
before either of the stores issued on CPU 2.


Furthermore, following a store by a load from the same device obviates the need
for the mmiowb(), because the load forces the store to complete before the load
is performed:

	CPU 1				CPU 2
	===============================	===============================
	spin_lock(Q)
	writel(0, ADDR)
	a = readl(DATA);
	spin_unlock(Q);
					spin_lock(Q);
					writel(4, ADDR);
					b = readl(DATA);
					spin_unlock(Q);


See Documentation/driver-api/device-io.rst for more information.


=================================
WHERE ARE MEMORY BARRIERS NEEDED?
=================================

Under normal operation, memory operation reordering is generally not going to
be a problem as a single-threaded linear piece of code will still appear to
work correctly, even if it's in an SMP kernel.  There are, however, four
circumstances in which reordering definitely _could_ be a problem:

 (*) Interprocessor interaction.

 (*) Atomic operations.

 (*) Accessing devices.

 (*) Interrupts.


INTERPROCESSOR INTERACTION
--------------------------

When there's a system with more than one processor, more than one CPU in the
system may be working on the same data set at the same time.  This can cause
synchronisation problems, and the usual way of dealing with them is to use
locks.  Locks, however, are quite expensive, and so it may be preferable to
operate without the use of a lock if at all possible.  In such a case
operations that affect both CPUs may have to be carefully ordered to prevent
a malfunction.

Consider, for example, the R/W semaphore slow path.  Here a waiting process is
queued on the semaphore, by virtue of it having a piece of its stack linked to
the semaphore's list of waiting processes:

	struct rw_semaphore {
		...
		spinlock_t lock;
		struct list_head waiters;
	};

	struct rwsem_waiter {
		struct list_head list;
		struct task_struct *task;
	};

To wake up a particular waiter, the up_read() or up_write() functions have to:

 (1) read the next pointer from this waiter's record to know as to where the
     next waiter record is;

 (2) read the pointer to the waiter's task structure;

 (3) clear the task pointer to tell the waiter it has been given the semaphore;

 (4) call wake_up_process() on the task; and

 (5) release the reference held on the waiter's task struct.

In other words, it has to perform this sequence of events:

	LOAD waiter->list.next;
	LOAD waiter->task;
	STORE waiter->task;
	CALL wakeup
	RELEASE task

and if any of these steps occur out of order, then the whole thing may
malfunction.

Once it has queued itself and dropped the semaphore lock, the waiter does not
get the lock again; it instead just waits for its task pointer to be cleared
before proceeding.  Since the record is on the waiter's stack, this means that
if the task pointer is cleared _before_ the next pointer in the list is read,
another CPU might start processing the waiter and might clobber the waiter's
stack before the up*() function has a chance to read the next pointer.

Consider then what might happen to the above sequence of events:

	CPU 1				CPU 2
	===============================	===============================
					down_xxx()
					Queue waiter
					Sleep
	up_yyy()
	LOAD waiter->task;
	STORE waiter->task;
					Woken up by other event
	<preempt>
					Resume processing
					down_xxx() returns
					call foo()
					foo() clobbers *waiter
	</preempt>
	LOAD waiter->list.next;
	--- OOPS ---

This could be dealt with using the semaphore lock, but then the down_xxx()
function has to needlessly get the spinlock again after being woken up.

The way to deal with this is to insert a general SMP memory barrier:

	LOAD waiter->list.next;
	LOAD waiter->task;
	smp_mb();
	STORE waiter->task;
	CALL wakeup
	RELEASE task

In this case, the barrier makes a guarantee that all memory accesses before the
barrier will appear to happen before all the memory accesses after the barrier
with respect to the other CPUs on the system.  It does _not_ guarantee that all
the memory accesses before the barrier will be complete by the time the barrier
instruction itself is complete.

On a UP system - where this wouldn't be a problem - the smp_mb() is just a
compiler barrier, thus making sure the compiler emits the instructions in the
right order without actually intervening in the CPU.  Since there's only one
CPU, that CPU's dependency ordering logic will take care of everything else.


ATOMIC OPERATIONS
-----------------

Whilst they are technically interprocessor interaction considerations, atomic
operations are noted specially as some of them imply full memory barriers and
some don't, but they're very heavily relied on as a group throughout the
kernel.

See Documentation/atomic_t.txt for more information.


ACCESSING DEVICES
-----------------

Many devices can be memory mapped, and so appear to the CPU as if they're just
a set of memory locations.  To control such a device, the driver usually has to
make the right memory accesses in exactly the right order.

However, having a clever CPU or a clever compiler creates a potential problem
in that the carefully sequenced accesses in the driver code won't reach the
device in the requisite order if the CPU or the compiler thinks it is more
efficient to reorder, combine or merge accesses - something that would cause
the device to malfunction.

Inside of the Linux kernel, I/O should be done through the appropriate accessor
routines - such as inb() or writel() - which know how to make such accesses
appropriately sequential.  Whilst this, for the most part, renders the explicit
use of memory barriers unnecessary, there are a couple of situations where they
might be needed:

 (1) On some systems, I/O stores are not strongly ordered across all CPUs, and
     so for _all_ general drivers locks should be used and mmiowb() must be
     issued prior to unlocking the critical section.

 (2) If the accessor functions are used to refer to an I/O memory window with
     relaxed memory access properties, then _mandatory_ memory barriers are
     required to enforce ordering.

See Documentation/driver-api/device-io.rst for more information.


INTERRUPTS
----------

A driver may be interrupted by its own interrupt service routine, and thus the
two parts of the driver may interfere with each other's attempts to control or
access the device.

This may be alleviated - at least in part - by disabling local interrupts (a
form of locking), such that the critical operations are all contained within
the interrupt-disabled section in the driver.  Whilst the driver's interrupt
routine is executing, the driver's core may not run on the same CPU, and its
interrupt is not permitted to happen again until the current interrupt has been
handled, thus the interrupt handler does not need to lock against that.

However, consider a driver that was talking to an ethernet card that sports an
address register and a data register.  If that driver's core talks to the card
under interrupt-disablement and then the driver's interrupt handler is invoked:

	LOCAL IRQ DISABLE
	writew(ADDR, 3);
	writew(DATA, y);
	LOCAL IRQ ENABLE
	<interrupt>
	writew(ADDR, 4);
	q = readw(DATA);
	</interrupt>

The store to the data register might happen after the second store to the
address register if ordering rules are sufficiently relaxed:

	STORE *ADDR = 3, STORE *ADDR = 4, STORE *DATA = y, q = LOAD *DATA


If ordering rules are relaxed, it must be assumed that accesses done inside an
interrupt disabled section may leak outside of it and may interleave with
accesses performed in an interrupt - and vice versa - unless implicit or
explicit barriers are used.

Normally this won't be a problem because the I/O accesses done inside such
sections will include synchronous load operations on strictly ordered I/O
registers that form implicit I/O barriers.  If this isn't sufficient then an
mmiowb() may need to be used explicitly.


A similar situation may occur between an interrupt routine and two routines
running on separate CPUs that communicate with each other.  If such a case is
likely, then interrupt-disabling locks should be used to guarantee ordering.


==========================
KERNEL I/O BARRIER EFFECTS
==========================

When accessing I/O memory, drivers should use the appropriate accessor
functions:

 (*) inX(), outX():

     These are intended to talk to I/O space rather than memory space, but
     that's primarily a CPU-specific concept.  The i386 and x86_64 processors
     do indeed have special I/O space access cycles and instructions, but many
     CPUs don't have such a concept.

     The PCI bus, amongst others, defines an I/O space concept which - on such
     CPUs as i386 and x86_64 - readily maps to the CPU's concept of I/O
     space.  However, it may also be mapped as a virtual I/O space in the CPU's
     memory map, particularly on those CPUs that don't support alternate I/O
     spaces.

     Accesses to this space may be fully synchronous (as on i386), but
     intermediary bridges (such as the PCI host bridge) may not fully honour
     that.

     They are guaranteed to be fully ordered with respect to each other.

     They are not guaranteed to be fully ordered with respect to other types of
     memory and I/O operation.

 (*) readX(), writeX():

     Whether these are guaranteed to be fully ordered and uncombined with
     respect to each other on the issuing CPU depends on the characteristics
     defined for the memory window through which they're accessing.  On later
     i386 architecture machines, for example, this is controlled by way of the
     MTRR registers.

     Ordinarily, these will be guaranteed to be fully ordered and uncombined,
     provided they're not accessing a prefetchable device.

     However, intermediary hardware (such as a PCI bridge) may indulge in
     deferral if it so wishes; to flush a store, a load from the same location
     is preferred[*], but a load from the same device or from configuration
     space should suffice for PCI.

     [*] NOTE! attempting to load from the same location as was written to may
	 cause a malfunction - consider the 16550 Rx/Tx serial registers for
	 example.

     Used with prefetchable I/O memory, an mmiowb() barrier may be required to
     force stores to be ordered.

     Please refer to the PCI specification for more information on interactions
     between PCI transactions.

 (*) readX_relaxed(), writeX_relaxed()

     These are similar to readX() and writeX(), but provide weaker memory
     ordering guarantees.  Specifically, they do not guarantee ordering with
     respect to normal memory accesses (e.g. DMA buffers) nor do they guarantee
     ordering with respect to LOCK or UNLOCK operations.  If the latter is
     required, an mmiowb() barrier can be used.  Note that relaxed accesses to
     the same peripheral are guaranteed to be ordered with respect to each
     other.

 (*) ioreadX(), iowriteX()

     These will perform appropriately for the type of access they're actually
     doing, be it inX()/outX() or readX()/writeX().


========================================
ASSUMED MINIMUM EXECUTION ORDERING MODEL
========================================

It has to be assumed that the conceptual CPU is weakly-ordered but that it will
maintain the appearance of program causality with respect to itself.  Some CPUs
(such as i386 or x86_64) are more constrained than others (such as powerpc or
frv), and so the most relaxed case (namely DEC Alpha) must be assumed outside
of arch-specific code.

This means that it must be considered that the CPU will execute its instruction
stream in any order it feels like - or even in parallel - provided that if an
instruction in the stream depends on an earlier instruction, then that
earlier instruction must be sufficiently complete[*] before the later
instruction may proceed; in other words: provided that the appearance of
causality is maintained.

 [*] Some instructions have more than one effect - such as changing the
     condition codes, changing registers or changing memory - and different
     instructions may depend on different effects.

A CPU may also discard any instruction sequence that winds up having no
ultimate effect.  For example, if two adjacent instructions both load an
immediate value into the same register, the first may be discarded.


Similarly, it has to be assumed that compiler might reorder the instruction
stream in any way it sees fit, again provided the appearance of causality is
maintained.


============================
THE EFFECTS OF THE CPU CACHE
============================

The way cached memory operations are perceived across the system is affected to
a certain extent by the caches that lie between CPUs and memory, and by the
memory coherence system that maintains the consistency of state in the system.

As far as the way a CPU interacts with another part of the system through the
caches goes, the memory system has to include the CPU's caches, and memory
barriers for the most part act at the interface between the CPU and its cache
(memory barriers logically act on the dotted line in the following diagram):

	    <--- CPU --->         :       <----------- Memory ----------->
	                          :
	+--------+    +--------+  :   +--------+    +-----------+
	|        |    |        |  :   |        |    |           |    +--------+
	|  CPU   |    | Memory |  :   | CPU    |    |           |    |        |
	|  Core  |--->| Access |----->| Cache  |<-->|           |    |        |
	|        |    | Queue  |  :   |        |    |           |--->| Memory |
	|        |    |        |  :   |        |    |           |    |        |
	+--------+    +--------+  :   +--------+    |           |    |        |
	                          :                 | Cache     |    +--------+
	                          :                 | Coherency |
	                          :                 | Mechanism |    +--------+
	+--------+    +--------+  :   +--------+    |           |    |	      |
	|        |    |        |  :   |        |    |           |    |        |
	|  CPU   |    | Memory |  :   | CPU    |    |           |--->| Device |
	|  Core  |--->| Access |----->| Cache  |<-->|           |    |        |
	|        |    | Queue  |  :   |        |    |           |    |        |
	|        |    |        |  :   |        |    |           |    +--------+
	+--------+    +--------+  :   +--------+    +-----------+
	                          :
	                          :

Although any particular load or store may not actually appear outside of the
CPU that issued it since it may have been satisfied within the CPU's own cache,
it will still appear as if the full memory access had taken place as far as the
other CPUs are concerned since the cache coherency mechanisms will migrate the
cacheline over to the accessing CPU and propagate the effects upon conflict.

The CPU core may execute instructions in any order it deems fit, provided the
expected program causality appears to be maintained.  Some of the instructions
generate load and store operations which then go into the queue of memory
accesses to be performed.  The core may place these in the queue in any order
it wishes, and continue execution until it is forced to wait for an instruction
to complete.

What memory barriers are concerned with is controlling the order in which
accesses cross from the CPU side of things to the memory side of things, and
the order in which the effects are perceived to happen by the other observers
in the system.

[!] Memory barriers are _not_ needed within a given CPU, as CPUs always see
their own loads and stores as if they had happened in program order.

[!] MMIO or other device accesses may bypass the cache system.  This depends on
the properties of the memory window through which devices are accessed and/or
the use of any special device communication instructions the CPU may have.


CACHE COHERENCY
---------------

Life isn't quite as simple as it may appear above, however: for while the
caches are expected to be coherent, there's no guarantee that that coherency
will be ordered.  This means that whilst changes made on one CPU will
eventually become visible on all CPUs, there's no guarantee that they will
become apparent in the same order on those other CPUs.


Consider dealing with a system that has a pair of CPUs (1 & 2), each of which
has a pair of parallel data caches (CPU 1 has A/B, and CPU 2 has C/D):

	            :
	            :                          +--------+
	            :      +---------+         |        |
	+--------+  : +--->| Cache A |<------->|        |
	|        |  : |    +---------+         |        |
	|  CPU 1 |<---+                        |        |
	|        |  : |    +---------+         |        |
	+--------+  : +--->| Cache B |<------->|        |
	            :      +---------+         |        |
	            :                          | Memory |
	            :      +---------+         | System |
	+--------+  : +--->| Cache C |<------->|        |
	|        |  : |    +---------+         |        |
	|  CPU 2 |<---+                        |        |
	|        |  : |    +---------+         |        |
	+--------+  : +--->| Cache D |<------->|        |
	            :      +---------+         |        |
	            :                          +--------+
	            :

Imagine the system has the following properties:

 (*) an odd-numbered cache line may be in cache A, cache C or it may still be
     resident in memory;

 (*) an even-numbered cache line may be in cache B, cache D or it may still be
     resident in memory;

 (*) whilst the CPU core is interrogating one cache, the other cache may be
     making use of the bus to access the rest of the system - perhaps to
     displace a dirty cacheline or to do a speculative load;

 (*) each cache has a queue of operations that need to be applied to that cache
     to maintain coherency with the rest of the system;

 (*) the coherency queue is not flushed by normal loads to lines already
     present in the cache, even though the contents of the queue may
     potentially affect those loads.

Imagine, then, that two writes are made on the first CPU, with a write barrier
between them to guarantee that they will appear to reach that CPU's caches in
the requisite order:

	CPU 1		CPU 2		COMMENT
	===============	===============	=======================================
					u == 0, v == 1 and p == &u, q == &u
	v = 2;
	smp_wmb();			Make sure change to v is visible before
					 change to p
	<A:modify v=2>			v is now in cache A exclusively
	p = &v;
	<B:modify p=&v>			p is now in cache B exclusively

The write memory barrier forces the other CPUs in the system to perceive that
the local CPU's caches have apparently been updated in the correct order.  But
now imagine that the second CPU wants to read those values:

	CPU 1		CPU 2		COMMENT
	===============	===============	=======================================
	...
			q = p;
			x = *q;

The above pair of reads may then fail to happen in the expected order, as the
cacheline holding p may get updated in one of the second CPU's caches whilst
the update to the cacheline holding v is delayed in the other of the second
CPU's caches by some other cache event:

	CPU 1		CPU 2		COMMENT
	===============	===============	=======================================
					u == 0, v == 1 and p == &u, q == &u
	v = 2;
	smp_wmb();
	<A:modify v=2>	<C:busy>
			<C:queue v=2>
	p = &v;		q = p;
			<D:request p>
	<B:modify p=&v>	<D:commit p=&v>
			<D:read p>
			x = *q;
			<C:read *q>	Reads from v before v updated in cache
			<C:unbusy>
			<C:commit v=2>

Basically, whilst both cachelines will be updated on CPU 2 eventually, there's
no guarantee that, without intervention, the order of update will be the same
as that committed on CPU 1.


To intervene, we need to interpolate a data dependency barrier or a read
barrier between the loads.  This will force the cache to commit its coherency
queue before processing any further requests:

	CPU 1		CPU 2		COMMENT
	===============	===============	=======================================
					u == 0, v == 1 and p == &u, q == &u
	v = 2;
	smp_wmb();
	<A:modify v=2>	<C:busy>
			<C:queue v=2>
	p = &v;		q = p;
			<D:request p>
	<B:modify p=&v>	<D:commit p=&v>
			<D:read p>
			smp_read_barrier_depends()
			<C:unbusy>
			<C:commit v=2>
			x = *q;
			<C:read *q>	Reads from v after v updated in cache


This sort of problem can be encountered on DEC Alpha processors as they have a
split cache that improves performance by making better use of the data bus.
Whilst most CPUs do imply a data dependency barrier on the read when a memory
access depends on a read, not all do, so it may not be relied on.

Other CPUs may also have split caches, but must coordinate between the various
cachelets for normal memory accesses.  The semantics of the Alpha removes the
need for coordination in the absence of memory barriers.


CACHE COHERENCY VS DMA
----------------------

Not all systems maintain cache coherency with respect to devices doing DMA.  In
such cases, a device attempting DMA may obtain stale data from RAM because
dirty cache lines may be resident in the caches of various CPUs, and may not
have been written back to RAM yet.  To deal with this, the appropriate part of
the kernel must flush the overlapping bits of cache on each CPU (and maybe
invalidate them as well).

In addition, the data DMA'd to RAM by a device may be overwritten by dirty
cache lines being written back to RAM from a CPU's cache after the device has
installed its own data, or cache lines present in the CPU's cache may simply
obscure the fact that RAM has been updated, until at such time as the cacheline
is discarded from the CPU's cache and reloaded.  To deal with this, the
appropriate part of the kernel must invalidate the overlapping bits of the
cache on each CPU.

See Documentation/cachetlb.txt for more information on cache management.


CACHE COHERENCY VS MMIO
-----------------------

Memory mapped I/O usually takes place through memory locations that are part of
a window in the CPU's memory space that has different properties assigned than
the usual RAM directed window.

Amongst these properties is usually the fact that such accesses bypass the
caching entirely and go directly to the device buses.  This means MMIO accesses
may, in effect, overtake accesses to cached memory that were emitted earlier.
A memory barrier isn't sufficient in such a case, but rather the cache must be
flushed between the cached memory write and the MMIO access if the two are in
any way dependent.


=========================
THE THINGS CPUS GET UP TO
=========================

A programmer might take it for granted that the CPU will perform memory
operations in exactly the order specified, so that if the CPU is, for example,
given the following piece of code to execute:

	a = READ_ONCE(*A);
	WRITE_ONCE(*B, b);
	c = READ_ONCE(*C);
	d = READ_ONCE(*D);
	WRITE_ONCE(*E, e);

they would then expect that the CPU will complete the memory operation for each
instruction before moving on to the next one, leading to a definite sequence of
operations as seen by external observers in the system:

	LOAD *A, STORE *B, LOAD *C, LOAD *D, STORE *E.


Reality is, of course, much messier.  With many CPUs and compilers, the above
assumption doesn't hold because:

 (*) loads are more likely to need to be completed immediately to permit
     execution progress, whereas stores can often be deferred without a
     problem;

 (*) loads may be done speculatively, and the result discarded should it prove
     to have been unnecessary;

 (*) loads may be done speculatively, leading to the result having been fetched
     at the wrong time in the expected sequence of events;

 (*) the order of the memory accesses may be rearranged to promote better use
     of the CPU buses and caches;

 (*) loads and stores may be combined to improve performance when talking to
     memory or I/O hardware that can do batched accesses of adjacent locations,
     thus cutting down on transaction setup costs (memory and PCI devices may
     both be able to do this); and

 (*) the CPU's data cache may affect the ordering, and whilst cache-coherency
     mechanisms may alleviate this - once the store has actually hit the cache
     - there's no guarantee that the coherency management will be propagated in
     order to other CPUs.

So what another CPU, say, might actually observe from the above piece of code
is:

	LOAD *A, ..., LOAD {*C,*D}, STORE *E, STORE *B

	(Where "LOAD {*C,*D}" is a combined load)


However, it is guaranteed that a CPU will be self-consistent: it will see its
_own_ accesses appear to be correctly ordered, without the need for a memory
barrier.  For instance with the following code:

	U = READ_ONCE(*A);
	WRITE_ONCE(*A, V);
	WRITE_ONCE(*A, W);
	X = READ_ONCE(*A);
	WRITE_ONCE(*A, Y);
	Z = READ_ONCE(*A);

and assuming no intervention by an external influence, it can be assumed that
the final result will appear to be:

	U == the original value of *A
	X == W
	Z == Y
	*A == Y

The code above may cause the CPU to generate the full sequence of memory
accesses:

	U=LOAD *A, STORE *A=V, STORE *A=W, X=LOAD *A, STORE *A=Y, Z=LOAD *A

in that order, but, without intervention, the sequence may have almost any
combination of elements combined or discarded, provided the program's view
of the world remains consistent.  Note that READ_ONCE() and WRITE_ONCE()
are -not- optional in the above example, as there are architectures
where a given CPU might reorder successive loads to the same location.
On such architectures, READ_ONCE() and WRITE_ONCE() do whatever is
necessary to prevent this, for example, on Itanium the volatile casts
used by READ_ONCE() and WRITE_ONCE() cause GCC to emit the special ld.acq
and st.rel instructions (respectively) that prevent such reordering.

The compiler may also combine, discard or defer elements of the sequence before
the CPU even sees them.

For instance:

	*A = V;
	*A = W;

may be reduced to:

	*A = W;

since, without either a write barrier or an WRITE_ONCE(), it can be
assumed that the effect of the storage of V to *A is lost.  Similarly:

	*A = Y;
	Z = *A;

may, without a memory barrier or an READ_ONCE() and WRITE_ONCE(), be
reduced to:

	*A = Y;
	Z = Y;

and the LOAD operation never appear outside of the CPU.


AND THEN THERE'S THE ALPHA
--------------------------

The DEC Alpha CPU is one of the most relaxed CPUs there is.  Not only that,
some versions of the Alpha CPU have a split data cache, permitting them to have
two semantically-related cache lines updated at separate times.  This is where
the data dependency barrier really becomes necessary as this synchronises both
caches with the memory coherence system, thus making it seem like pointer
changes vs new data occur in the right order.

The Alpha defines the Linux kernel's memory barrier model.

See the subsection on "Cache Coherency" above.


VIRTUAL MACHINE GUESTS
----------------------

Guests running within virtual machines might be affected by SMP effects even if
the guest itself is compiled without SMP support.  This is an artifact of
interfacing with an SMP host while running an UP kernel.  Using mandatory
barriers for this use-case would be possible but is often suboptimal.

To handle this case optimally, low-level virt_mb() etc macros are available.
These have the same effect as smp_mb() etc when SMP is enabled, but generate
identical code for SMP and non-SMP systems.  For example, virtual machine guests
should use virt_mb() rather than smp_mb() when synchronizing against a
(possibly SMP) host.

These are equivalent to smp_mb() etc counterparts in all other respects,
in particular, they do not control MMIO effects: to control
MMIO effects, use mandatory barriers.


============
EXAMPLE USES
============

CIRCULAR BUFFERS
----------------

Memory barriers can be used to implement circular buffering without the need
of a lock to serialise the producer with the consumer.  See:

	Documentation/circular-buffers.txt

for details.


==========
REFERENCES
==========

Alpha AXP Architecture Reference Manual, Second Edition (Sites & Witek,
Digital Press)
	Chapter 5.2: Physical Address Space Characteristics
	Chapter 5.4: Caches and Write Buffers
	Chapter 5.5: Data Sharing
	Chapter 5.6: Read/Write Ordering

AMD64 Architecture Programmer's Manual Volume 2: System Programming
	Chapter 7.1: Memory-Access Ordering
	Chapter 7.4: Buffering and Combining Memory Writes

IA-32 Intel Architecture Software Developer's Manual, Volume 3:
System Programming Guide
	Chapter 7.1: Locked Atomic Operations
	Chapter 7.2: Memory Ordering
	Chapter 7.4: Serializing Instructions

The SPARC Architecture Manual, Version 9
	Chapter 8: Memory Models
	Appendix D: Formal Specification of the Memory Models
	Appendix J: Programming with the Memory Models

UltraSPARC Programmer Reference Manual
	Chapter 5: Memory Accesses and Cacheability
	Chapter 15: Sparc-V9 Memory Models

UltraSPARC III Cu User's Manual
	Chapter 9: Memory Models

UltraSPARC IIIi Processor User's Manual
	Chapter 8: Memory Models

UltraSPARC Architecture 2005
	Chapter 9: Memory
	Appendix D: Formal Specifications of the Memory Models

UltraSPARC T1 Supplement to the UltraSPARC Architecture 2005
	Chapter 8: Memory Models
	Appendix F: Caches and Cache Coherency

Solaris Internals, Core Kernel Architecture, p63-68:
	Chapter 3.3: Hardware Considerations for Locks and
			Synchronization

Unix Systems for Modern Architectures, Symmetric Multiprocessing and Caching
for Kernel Programmers:
	Chapter 13: Other Memory Models

Intel Itanium Architecture Software Developer's Manual: Volume 1:
	Section 2.6: Speculation
	Section 4.4: Memory Access
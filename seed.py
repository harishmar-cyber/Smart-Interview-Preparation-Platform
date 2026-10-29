import io
import json
import os
import sys
from datetime import datetime, timedelta

# Fix Windows console unicode printing
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app import create_app
from models import (
    db, User, Category, Question, MockTest, TestQuestion,
    CodingProblem, CodingSubmission, HRQuestion, HRPractice,
    TestAttempt, AttemptAnswer, ActivityLog, Bookmark
)
from services.scoring_service import grade_test_attempt
from services.recommendation_service import generate_recommendations

def run_seed():
    app = create_app()
    with app.app_context():
        print("[*] Seeding Smart Interview Preparation Platform database...")
        db.create_all()

        # Clear existing data in reverse dependency order
        print("   Clearing existing records...")
        ActivityLog.query.delete()
        Bookmark.query.delete()
        AttemptAnswer.query.delete()
        TestAttempt.query.delete()
        TestQuestion.query.delete()
        MockTest.query.delete()
        Question.query.delete()
        CodingSubmission.query.delete()
        CodingProblem.query.delete()
        HRPractice.query.delete()
        HRQuestion.query.delete()
        Category.query.delete()
        User.query.delete()
        db.session.commit()

        # 1. USERS
        print("   Creating Admin and Student accounts...")
        admin = User(
            full_name="System Administrator",
            email=os.environ.get('ADMIN_EMAIL', 'admin@smartprep.com'),
            role="admin",
            preferred_job_role="Engineering Manager",
            education="M.Tech Computer Science",
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=30)
        )
        admin.set_password(os.environ.get('ADMIN_PASSWORD', 'Admin@123'))

        student = User(
            full_name="Harish Marimuthu",
            email="student@smartprep.com",
            role="student",
            preferred_job_role="Full Stack Developer",
            education="B.Tech Computer Science & Engineering",
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=10)
        )
        student.set_password("Student@123")

        db.session.add(admin)
        db.session.add(student)
        db.session.commit()

        # 2. CATEGORIES
        print("   Creating 10 Core Categories...")
        categories_data = [
            {"name": "Java", "description": "Core Java, OOP principles, Collections framework, JVM, Multi-threading and Exception handling.", "icon": "fa-coffee", "color": "#EA580C"},
            {"name": "Python", "description": "Python data structures, decorators, generators, OOP concepts, list comprehensions, and memory model.", "icon": "fa-brands fa-python", "color": "#0284C7"},
            {"name": "C/C++", "description": "Pointers, memory allocation, STL containers, references, virtual functions, and compilation stages.", "icon": "fa-microchip", "color": "#4F46E5"},
            {"name": "DBMS", "description": "Relational algebra, SQL queries, Normalization (1NF-BCNF), ACID properties, Transactions, and Indexing.", "icon": "fa-database", "color": "#059669"},
            {"name": "Operating Systems", "description": "Process scheduling, Deadlocks, Virtual memory, Paging, Semaphores, and Thread synchronization.", "icon": "fa-server", "color": "#D97706"},
            {"name": "Computer Networks", "description": "OSI & TCP/IP models, routing protocols, HTTP/HTTPS, DNS, subnetting, TCP handshake, and socket programming.", "icon": "fa-network-wired", "color": "#7C3AED"},
            {"name": "Object-Oriented Programming", "description": "Encapsulation, Inheritance, Polymorphism, Abstraction, SOLID principles, and Design patterns.", "icon": "fa-cubes", "color": "#DB2777"},
            {"name": "Data Structures and Algorithms", "description": "Arrays, Linked Lists, Stacks, Queues, Binary Trees, Graphs, Sorting, Dynamic Programming, and Big-O notation.", "icon": "fa-sitemap", "color": "#2563EB"},
            {"name": "Aptitude", "description": "Quantitative aptitude, percentages, profit and loss, time and work, speed-distance, permutation, and logical reasoning.", "icon": "fa-brain", "color": "#E11D48"},
            {"name": "HR Interview", "description": "Behavioral questions, situational judgment, STAR method, culture fit, strengths, weaknesses, and career objectives.", "icon": "fa-user-tie", "color": "#0D9488"},
        ]

        cats_map = {}
        for cdata in categories_data:
            cat = Category(
                name=cdata['name'],
                description=cdata['description'],
                icon=cdata['icon'],
                color=cdata['color']
            )
            db.session.add(cat)
            db.session.flush()
            cats_map[cat.name] = cat

        # 3. INTERVIEW QUESTIONS (70 meaningful questions across all 10 categories)
        print("   Creating 70+ Curated Interview Questions...")
        raw_questions = [
            # Java
            {
                "cat": "Java",
                "text": "What is the primary difference between String, StringBuilder, and StringBuffer in Java?",
                "diff": "Medium",
                "a": "String is mutable, whereas StringBuilder and StringBuffer are immutable.",
                "b": "String is immutable; StringBuffer is mutable and thread-safe; StringBuilder is mutable and not thread-safe.",
                "c": "StringBuilder is thread-safe and synchronous; StringBuffer is asynchronous.",
                "d": "All three have identical performance and memory overhead.",
                "ans": "B",
                "exp": "String objects are immutable in Java. StringBuffer is mutable and synchronized (thread-safe). StringBuilder is mutable, unsynchronized, and faster in single-threaded operations."
            },
            {
                "cat": "Java",
                "text": "Which memory area in the JVM is shared among all running threads?",
                "diff": "Medium",
                "a": "JVM Stack",
                "b": "Program Counter (PC) Register",
                "c": "Heap Area and Method Area",
                "d": "Native Method Stack",
                "ans": "C",
                "exp": "The Heap and Method areas are created at JVM startup and shared across all threads. The Java thread stacks and PC registers are private to individual threads."
            },
            {
                "cat": "Java",
                "text": "Can a constructor in Java be declared as final, static, or abstract?",
                "diff": "Easy",
                "a": "Yes, all three modifiers are valid.",
                "b": "Only static is allowed.",
                "c": "No, constructors cannot be final, static, or abstract.",
                "d": "Only final is allowed to prevent overriding.",
                "ans": "C",
                "exp": "Constructors are never inherited, so they cannot be overridden (making final meaningless), cannot be static because they operate on instance creation, and cannot be abstract as they must have an implementation body."
            },
            {
                "cat": "Java",
                "text": "What is the time complexity of searching an element in a java.util.HashMap in the average case?",
                "diff": "Easy",
                "a": "O(log n)",
                "b": "O(1)",
                "c": "O(n)",
                "d": "O(n log n)",
                "ans": "B",
                "exp": "HashMap computes the hash code of the key to jump directly to the target bucket in O(1) average time complexity."
            },
            {
                "cat": "Java",
                "text": "What happens when an exception is thrown inside a try block with a matching catch block and a finally block?",
                "diff": "Easy",
                "a": "The finally block executes before the catch block.",
                "b": "The finally block only executes if the catch block throws another exception.",
                "c": "The catch block executes first, and then the finally block always executes.",
                "d": "The finally block is bypassed if an exception is handled.",
                "ans": "C",
                "exp": "The catch block handles the exception first, and the finally block is guaranteed to execute regardless of whether an exception occurred or was handled."
            },
            {
                "cat": "Java",
                "text": "What does the 'transient' keyword indicate in Java serialization?",
                "diff": "Medium",
                "a": "The variable will be stored in permanent non-volatile memory.",
                "b": "The variable will not be serialized when saving object state.",
                "c": "The variable is synchronized across distributed nodes.",
                "d": "The variable cannot be accessed by external classes.",
                "ans": "B",
                "exp": "When a field is marked with the transient keyword, the JVM skips it during object serialization, and it resets to its default value upon deserialization."
            },
            {
                "cat": "Java",
                "text": "What is the difference between fail-fast and fail-safe iterators in Java collections?",
                "diff": "Hard",
                "a": "Fail-fast iterators throw ConcurrentModificationException if the collection is modified during iteration; fail-safe iterators work on a clone.",
                "b": "Fail-fast iterators ignore concurrent modifications, whereas fail-safe iterators terminate the process.",
                "c": "Fail-fast iterators are thread-safe, whereas fail-safe iterators are not.",
                "d": "Fail-safe is only supported by primitive array iterators.",
                "ans": "A",
                "exp": "Fail-fast iterators (like ArrayList, HashMap) immediately throw ConcurrentModificationException upon structural modification. Fail-safe iterators (like CopyOnWriteArrayList) traverse a copy of the collection."
            },

            # Python
            {
                "cat": "Python",
                "text": "How does the Global Interpreter Lock (GIL) affect Python multi-threading?",
                "diff": "Medium",
                "a": "It prevents multiple threads from accessing distinct memory spaces.",
                "b": "It allows true parallelism on multi-core CPUs for CPU-bound tasks.",
                "c": "It ensures only one thread executes Python bytecode at a time, preventing true CPU-bound parallelism in CPython.",
                "d": "It automatically converts recursive functions to iterative ones.",
                "ans": "C",
                "exp": "The CPython GIL is a mutex that prevents multiple native threads from executing Python bytecodes concurrently, limiting CPU-bound multi-threaded parallelism."
            },
            {
                "cat": "Python",
                "text": "What is the difference between list.append() and list.extend() in Python?",
                "diff": "Easy",
                "a": "append() adds the argument as a single element; extend() iterates over its argument adding each item individually.",
                "b": "append() merges two lists; extend() creates a nested tuple.",
                "c": "extend() returns a new list; append() operates in-place.",
                "d": "There is no functional difference.",
                "ans": "A",
                "exp": "append(x) inserts x as a single element at the end of the list. extend(iterable) unpacks each element from the iterable and appends them sequentially."
            },
            {
                "cat": "Python",
                "text": "What is the output of `bool([])`, `bool({})`, and `bool('False')` in Python?",
                "diff": "Easy",
                "a": "True, True, False",
                "b": "False, False, False",
                "c": "False, False, True",
                "d": "True, False, True",
                "ans": "C",
                "exp": "Empty sequences and collections ([], {}) evaluate to falsy (False). Any non-empty string, including 'False', evaluates to True."
            },
            {
                "cat": "Python",
                "text": "What is a Python decorator and what syntax is used to apply it?",
                "diff": "Medium",
                "a": "A decorator modifies HTML rendering using {{ ... }}.",
                "b": "A function that takes another function as an argument and extends its behavior without modifying it, applied with @decorator.",
                "c": "A class method designated with #decorator.",
                "d": "A special comment syntax for documentation.",
                "ans": "B",
                "exp": "Decorators are callable higher-order functions that wrap another function to extend its behavior dynamically, applied using the @decorator syntax."
            },
            {
                "cat": "Python",
                "text": "How does Python handle memory management and garbage collection?",
                "diff": "Hard",
                "a": "Only manual deallocation using `del` keyword.",
                "b": "Strictly mark-and-sweep algorithm executed at application termination.",
                "c": "Primary reference counting supplemented by a cyclic generational garbage collector.",
                "d": "Direct OS page allocation without internal heap structures.",
                "ans": "C",
                "exp": "CPython uses reference counting as its main garbage collection technique, complemented by a 3-generation cyclic garbage collector to detect circular reference loops."
            },
            {
                "cat": "Python",
                "text": "What is the purpose of the `yield` keyword in a Python function?",
                "diff": "Medium",
                "a": "It pauses the execution and turns the function into a generator returning values one at a time.",
                "b": "It terminates the loop and raises StopIteration immediately.",
                "c": "It forces thread context switching to the OS scheduler.",
                "d": "It returns a deep copy of all local variables.",
                "ans": "A",
                "exp": "The yield statement turns a function into a generator factory, producing values lazily on demand while maintaining state across invocations."
            },
            {
                "cat": "Python",
                "text": "What is the difference between shallow copy and deep copy in Python?",
                "diff": "Medium",
                "a": "Shallow copy duplicates recursive nested objects; deep copy copies top-level references only.",
                "b": "Shallow copy copies the outer object but inserts references to inner nested objects; deep copy recursively copies all nested objects.",
                "c": "Deep copy only applies to immutable types like tuples and strings.",
                "d": "Shallow copy is performed with copy.deepcopy(); deep copy is performed with copy.copy().",
                "ans": "B",
                "exp": "copy.copy() creates a new collection object and populates it with references to the original child items. copy.deepcopy() recursively duplicates all referenced items."
            },

            # C / C++
            {
                "cat": "C/C++",
                "text": "What is the difference between malloc() and calloc() in C?",
                "diff": "Easy",
                "a": "malloc() allocates memory from stack; calloc() allocates from heap.",
                "b": "malloc() does not initialize memory (leaves garbage); calloc() initializes allocated memory bytes to zero.",
                "c": "malloc() requires two arguments; calloc() takes one argument.",
                "d": "calloc() cannot be freed using free().",
                "ans": "B",
                "exp": "malloc(size) allocates contiguous bytes leaving memory uninitialized. calloc(num, size) allocates memory and initializes all allocated bytes to zero."
            },
            {
                "cat": "C/C++",
                "text": "What happens if a base class destructor is NOT declared as virtual in C++ and a derived object is deleted via a base pointer?",
                "diff": "Medium",
                "a": "The derived class destructor is called followed by the base class destructor.",
                "b": "Undefined behavior occurs, typically causing a memory leak because derived class cleanup is skipped.",
                "c": "A compilation error occurs immediately.",
                "d": "The base class destructor is skipped entirely.",
                "ans": "B",
                "exp": "If the base destructor is not virtual, deleting through a base pointer causes static binding, executing only the base destructor and leaving derived resources uncleaned (memory leak / undefined behavior)."
            },
            {
                "cat": "C/C++",
                "text": "What is a dangling pointer in C/C++?",
                "diff": "Easy",
                "a": "A pointer that points to a memory location that has been deallocated or freed.",
                "b": "A pointer initialized to NULL or nullptr.",
                "c": "A pointer that points to an array of pointers.",
                "d": "A pointer whose address cannot be modified.",
                "ans": "A",
                "exp": "A dangling pointer occurs when the memory it references has been released or freed, but the pointer still holds the old memory address."
            },
            {
                "cat": "C/C++",
                "text": "What is the difference between a pointer and a reference in C++?",
                "diff": "Medium",
                "a": "References can be NULL and reassigned; pointers cannot be reassigned.",
                "b": "Pointers can be NULL and reassigned to point elsewhere; references must be initialized upon declaration and cannot be reseated.",
                "c": "References have their own independent memory address distinct from the referent.",
                "d": "Pointers cannot perform arithmetic; references can.",
                "ans": "B",
                "exp": "A reference is an alias for an existing object and cannot be null or rebound to another object after initialization. A pointer stores an address and can be reassigned or set to nullptr."
            },
            {
                "cat": "C/C++",
                "text": "What are the four compilation stages of a C program?",
                "diff": "Medium",
                "a": "Lexing, Parsing, Optimization, Packaging",
                "b": "Preprocessing, Compiling, Assembling, Linking",
                "c": "Interpretation, Bytecode generation, JIT, Execution",
                "d": "Pre-linking, Compilation, Verification, Archival",
                "ans": "B",
                "exp": "The standard compilation pipeline consists of Preprocessing (#include, macros), Compilation (to assembly code), Assembly (to machine code/object file .o), and Linking (combining object files and libraries to executable)."
            },
            {
                "cat": "C/C++",
                "text": "What is memory fragmentation and how do you mitigate it in systems programming?",
                "diff": "Hard",
                "a": "When CPU cache runs out of L1 lines; solved by overclocking.",
                "b": "When available memory is split into small non-contiguous blocks; mitigated using memory pools or slab allocators.",
                "c": "When stack memory overflows into heap; mitigated by increasing stack limit.",
                "d": "When pointers overflow 32-bit boundaries; solved by 64-bit casting.",
                "ans": "B",
                "exp": "External fragmentation occurs when total free memory is sufficient, but divided into small non-contiguous chunks. Custom memory allocators (like slab allocators or memory pools) mitigate this by reusing fixed-size chunks."
            },
            {
                "cat": "C/C++",
                "text": "In C++, what does the `explicit` keyword on a single-argument constructor prevent?",
                "diff": "Medium",
                "a": "It prevents inheritance by derived classes.",
                "b": "It prevents implicit conversions and copy-initialization.",
                "c": "It enforces strict compile-time template instantiation.",
                "d": "It stops the compiler from generating default destructors.",
                "ans": "B",
                "exp": "The explicit specifier prevents the compiler from using the single-parameter constructor for implicit type conversions and assignment copy-initialization."
            },

            # DBMS
            {
                "cat": "DBMS",
                "text": "What do the letters in ACID stand for in database transaction management?",
                "diff": "Easy",
                "a": "Accuracy, Consistency, Integrity, Durability",
                "b": "Atomicity, Consistency, Isolation, Durability",
                "c": "Availability, Concurrency, Indexing, Decoupling",
                "d": "Authentication, Cryptography, Isolation, Delegation",
                "ans": "B",
                "exp": "ACID properties: Atomicity (all-or-nothing), Consistency (preserves database rules), Isolation (independent transactions), and Durability (committed changes persist)."
            },
            {
                "cat": "DBMS",
                "text": "What is the difference between TRUNCATE and DELETE statements in SQL?",
                "diff": "Easy",
                "a": "DELETE is a DDL command; TRUNCATE is a DML command.",
                "b": "TRUNCATE is a DDL command that deallocates data pages without logging individual row deletions; DELETE is DML and logs each row deletion.",
                "c": "DELETE removes table structure; TRUNCATE preserves table schema.",
                "d": "TRUNCATE allows a WHERE clause; DELETE deletes the whole table.",
                "ans": "B",
                "exp": "TRUNCATE is a fast DDL command that resets the table by deallocating pages and cannot use a WHERE clause. DELETE is a DML command that evaluates WHERE conditions and logs each row deletion."
            },
            {
                "cat": "DBMS",
                "text": "What is the minimum requirement for a relation to be in Boyce-Codd Normal Form (BCNF)?",
                "diff": "Hard",
                "a": "Every non-prime attribute must depend on the primary key.",
                "b": "It must be in 3NF and for every functional dependency X -> Y, X must be a super key.",
                "c": "It must eliminate all multi-valued dependencies.",
                "d": "It must have composite primary keys only.",
                "ans": "B",
                "exp": "A relation is in BCNF if and only if for every non-trivial functional dependency X -> Y, X is a super key of the relation."
            },
            {
                "cat": "DBMS",
                "text": "What is the difference between clustered and non-clustered indexes?",
                "diff": "Medium",
                "a": "A table can have multiple clustered indexes, but only one non-clustered index.",
                "b": "A clustered index physically sorts and stores table rows in order; non-clustered indexes store a pointer structure pointing to the data rows.",
                "c": "Clustered indexes are slower than non-clustered indexes for range queries.",
                "d": "Non-clustered indexes are stored in the heap; clustered indexes in RAM.",
                "ans": "B",
                "exp": "A clustered index defines the physical order of data in the table (hence only one per table). A non-clustered index creates a separate B+ tree whose leaf nodes contain pointers to data rows."
            },
            {
                "cat": "DBMS",
                "text": "What is a 'Dirty Read' in database concurrency control?",
                "diff": "Medium",
                "a": "A transaction reads uncommitted changes made by another active transaction that may later rollback.",
                "b": "A transaction re-reads data and finds that new rows were inserted by another transaction.",
                "c": "A transaction reads corrupted disk blocks.",
                "d": "A query executes on unindexed foreign keys.",
                "ans": "A",
                "exp": "A Dirty Read occurs at Read Uncommitted isolation level when Transaction A reads modifications made by Transaction B before Transaction B commits. If Transaction B aborts/rolls back, Transaction A worked with invalid data."
            },
            {
                "cat": "DBMS",
                "text": "Which SQL clause is used to filter aggregated group results?",
                "diff": "Easy",
                "a": "WHERE",
                "b": "HAVING",
                "c": "ORDER BY",
                "d": "GROUP FILTER",
                "ans": "B",
                "exp": "WHERE filters rows before aggregation. HAVING filters grouped rows after aggregate functions (COUNT, SUM, AVG) are computed."
            },
            {
                "cat": "DBMS",
                "text": "What is the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN?",
                "diff": "Easy",
                "a": "INNER JOIN returns matching rows; LEFT JOIN returns all left rows plus matching right rows; FULL OUTER JOIN returns all rows from both tables.",
                "b": "LEFT JOIN only returns non-matching rows.",
                "c": "FULL OUTER JOIN is identical to CROSS JOIN.",
                "d": "INNER JOIN returns all rows regardless of condition.",
                "ans": "A",
                "exp": "INNER JOIN selects records with matching values in both tables. LEFT JOIN returns all records from the left table and matched right records. FULL OUTER JOIN returns all records when there is a match in left or right."
            },

            # Operating Systems
            {
                "cat": "Operating Systems",
                "text": "What are the four necessary conditions for a Deadlock to occur (Coffman conditions)?",
                "diff": "Medium",
                "a": "Paging, Segmentation, Swapping, Thrashing",
                "b": "Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait",
                "c": "Preemption, Starvation, Aging, Context Switching",
                "d": "Multiprocessing, Multithreading, Schedulability, Atomicity",
                "ans": "B",
                "exp": "The Coffman conditions are: Mutual Exclusion (non-shareable resources), Hold and Wait (holding a resource while waiting for another), No Preemption (resources cannot be forcibly taken), and Circular Wait."
            },
            {
                "cat": "Operating Systems",
                "text": "What causes 'Thrashing' in an operating system with virtual memory?",
                "diff": "Medium",
                "a": "When CPU clock frequency exceeds thermal limits.",
                "b": "When excessive page faulting occurs, causing the OS to spend more time swapping pages than executing instructions.",
                "c": "When multiple processes access the disk controller simultaneously.",
                "d": "When the kernel stack overflows into user space.",
                "ans": "B",
                "exp": "Thrashing occurs when the system lacks enough physical frames to satisfy the working sets of active processes, causing continuous page fault handling and severely degrading CPU utilization."
            },
            {
                "cat": "Operating Systems",
                "text": "What is the fundamental difference between a Process and a Thread?",
                "diff": "Easy",
                "a": "Processes share memory; threads have separate address spaces.",
                "b": "A process has its own independent address space and resources; threads within the same process share code, data, and open files while having their own stack and registers.",
                "c": "A thread cannot be scheduled by the OS.",
                "d": "Threads run on separate machines; processes run locally.",
                "ans": "B",
                "exp": "A process is an execution unit with isolated memory address space. Threads are lightweight execution units within a process that share address space and resources while maintaining their own PC, registers, and stack."
            },
            {
                "cat": "Operating Systems",
                "text": "Which CPU scheduling algorithm is provably optimal in minimizing average waiting time?",
                "diff": "Medium",
                "a": "First Come First Served (FCFS)",
                "b": "Round Robin (RR)",
                "c": "Shortest Job First (SJF) / Shortest Remaining Time First (SRTF)",
                "d": "Priority Scheduling without preemption",
                "ans": "C",
                "exp": "SJF (or SRTF in preemptive cases) gives the lowest average waiting time for a given set of stationary processes by executing the shortest burst time first."
            },
            {
                "cat": "Operating Systems",
                "text": "What is the purpose of the Translation Lookaside Buffer (TLB)?",
                "diff": "Hard",
                "a": "A high-speed hardware cache used to reduce the time taken to translate virtual page addresses to physical frame addresses.",
                "b": "A software buffer that queues network packets for socket delivery.",
                "c": "A disk block buffer for asynchronous writes.",
                "d": "A register file for holding intermediate arithmetic results.",
                "ans": "A",
                "exp": "The TLB is an associative cache located on the CPU Memory Management Unit (MMU) that stores recent virtual-to-physical address translations to avoid multi-level page table lookups in RAM."
            },
            {
                "cat": "Operating Systems",
                "text": "What is the difference between a binary semaphore and a mutex lock?",
                "diff": "Medium",
                "a": "They are exactly identical in all implementations.",
                "b": "A mutex incorporates ownership semantics (only the thread that locked it can unlock it), whereas a semaphore has no ownership and can be signaled by any thread.",
                "c": "Semaphores cannot protect critical sections.",
                "d": "Mutexes can only be implemented in user space.",
                "ans": "B",
                "exp": "A mutex is a locking mechanism with ownership (the locker must unlock it). A binary semaphore is a signaling mechanism without ownership (any thread can call sem_post to wake a waiter)."
            },
            {
                "cat": "Operating Systems",
                "text": "What is the role of a system call (syscall) in modern operating systems?",
                "diff": "Easy",
                "a": "To allow user-mode applications to request privileged services from the operating system kernel.",
                "b": "To compile source code into machine bytecode.",
                "c": "To restart peripheral hardware devices.",
                "d": "To debug runtime heap corruption.",
                "ans": "A",
                "exp": "A system call provides the programmatic interface between a user-space application and the protected kernel, switching the CPU from user mode to kernel mode via software interrupts."
            },

            # Computer Networks
            {
                "cat": "Computer Networks",
                "text": "What are the three steps of the TCP Three-Way Handshake connection establishment?",
                "diff": "Easy",
                "a": "PING -> PONG -> ACK",
                "b": "SYN -> SYN-ACK -> ACK",
                "c": "CONNECT -> ACCEPT -> READY",
                "d": "HELLO -> VERIFY -> CONNECT",
                "ans": "B",
                "exp": "TCP connection establishment: 1. Client sends SYN (synchronize sequence number). 2. Server responds with SYN-ACK. 3. Client replies with ACK (acknowledge)."
            },
            {
                "cat": "Computer Networks",
                "text": "What is the primary difference between TCP and UDP at the Transport layer?",
                "diff": "Easy",
                "a": "TCP is connectionless and fast; UDP is connection-oriented and reliable.",
                "b": "TCP is connection-oriented, reliable with flow and congestion control; UDP is connectionless, unreliable, and lightweight.",
                "c": "UDP guarantees packet order; TCP does not.",
                "d": "UDP operates at layer 7; TCP operates at layer 4.",
                "ans": "B",
                "exp": "TCP provides reliable, sequenced byte streams with retransmission, flow control, and congestion avoidance. UDP provides fast, best-effort message delivery without acknowledgments or connection state."
            },
            {
                "cat": "Computer Networks",
                "text": "In CIDR notation, how many usable host IP addresses are available in a /24 subnet?",
                "diff": "Easy",
                "a": "256",
                "b": "254",
                "c": "128",
                "d": "512",
                "ans": "B",
                "exp": "A /24 subnet provides 32 - 24 = 8 host bits, yielding 2^8 = 256 total IP addresses. Subtracting 2 (network address and broadcast address) leaves 254 usable host addresses."
            },
            {
                "cat": "Computer Networks",
                "text": "What is the purpose of the Domain Name System (DNS)?",
                "diff": "Easy",
                "a": "To assign MAC addresses to NIC hardware.",
                "b": "To translate human-readable domain names (e.g., example.com) into machine-readable IP addresses.",
                "c": "To encrypt traffic between clients and web servers.",
                "d": "To monitor router bandwidth congestion.",
                "ans": "B",
                "exp": "DNS serves as the internet's telephone book, translating alphanumeric domain names like 'google.com' into numerical IP addresses like '142.250.190.46'."
            },
            {
                "cat": "Computer Networks",
                "text": "How does HTTPS establish a secure session between client and server?",
                "diff": "Medium",
                "a": "Using TLS handshake with asymmetric cryptography for key exchange and symmetric cryptography for session data encryption.",
                "b": "By hashing packet headers with MD5.",
                "c": "By running standard HTTP over an unencrypted UDP tunnel.",
                "d": "Using symmetric keys pre-shared during operating system installation.",
                "ans": "A",
                "exp": "HTTPS uses the TLS handshake: the server proves identity via an SSL/TLS certificate, asymmetric cryptography (RSA/ECDH) negotiates a shared session key, and symmetric cryptography (AES) encrypts session traffic."
            },
            {
                "cat": "Computer Networks",
                "text": "What protocol resolves an IP address to a physical MAC address on a local area network?",
                "diff": "Easy",
                "a": "DNS",
                "b": "DHCP",
                "c": "ARP (Address Resolution Protocol)",
                "d": "ICMP",
                "ans": "C",
                "exp": "ARP broadcasts a query asking 'Who has this IP address?' on the local layer 2 segment, and the host with that IP replies with its 48-bit MAC address."
            },
            {
                "cat": "Computer Networks",
                "text": "What is the difference between HTTP/1.1 and HTTP/2?",
                "diff": "Hard",
                "a": "HTTP/2 introduces binary framing, multiplexing over a single TCP connection, header compression (HPACK), and server push.",
                "b": "HTTP/2 runs exclusively over UDP without handshakes.",
                "c": "HTTP/2 deprecated TLS encryption.",
                "d": "HTTP/1.1 supports multiple simultaneous requests per connection without head-of-line blocking.",
                "ans": "A",
                "exp": "HTTP/2 converts textual HTTP/1.1 into binary frames, enabling multiple bidirectional request/response streams over one TCP socket without head-of-line blocking, with HPACK compression."
            },

            # Object-Oriented Programming
            {
                "cat": "Object-Oriented Programming",
                "text": "What are the four fundamental pillars of Object-Oriented Programming?",
                "diff": "Easy",
                "a": "Compilation, Interpretation, Linking, Loading",
                "b": "Encapsulation, Abstraction, Inheritance, Polymorphism",
                "c": "Modularity, Scalability, Concurrency, Persistence",
                "d": "Iteration, Recursion, Branching, Selection",
                "ans": "B",
                "exp": "The four OOP principles are: Encapsulation (bundling data and methods), Abstraction (hiding implementation complexity), Inheritance (reusing code across hierarchy), and Polymorphism (many forms/overriding)."
            },
            {
                "cat": "Object-Oriented Programming",
                "text": "What is the difference between Method Overloading and Method Overriding?",
                "diff": "Easy",
                "a": "Overloading occurs at runtime across parent-child classes; overriding occurs at compile time in the same class.",
                "b": "Overloading occurs in the same class with same name but different parameter signatures (compile-time polymorphism); Overriding redefines a superclass method in a subclass with identical signature (runtime polymorphism).",
                "c": "Overriding requires different return types; overloading requires identical return types.",
                "d": "They are synonymous terms.",
                "ans": "B",
                "exp": "Method Overloading is static/compile-time polymorphism where methods have the same name but different parameter lists. Overriding is dynamic/runtime polymorphism where a subclass provides a specific implementation of a superclass method."
            },
            {
                "cat": "Object-Oriented Programming",
                "text": "What does the 'L' in the SOLID design principles stand for?",
                "diff": "Medium",
                "a": "Lazy Initialization Principle",
                "b": "Liskov Substitution Principle",
                "c": "Linear Inheritance Principle",
                "d": "Loose Coupling Principle",
                "ans": "B",
                "exp": "Liskov Substitution Principle (LSP) states that objects of a superclass should be replaceable with objects of its subclasses without breaking application correctness."
            },
            {
                "cat": "Object-Oriented Programming",
                "text": "What is the key difference between an Abstract Class and an Interface?",
                "diff": "Medium",
                "a": "A class can implement only one interface, but inherit multiple abstract classes.",
                "b": "An abstract class can maintain state (instance variables) and constructors, whereas interfaces traditionally define contracts without instance state (supporting multiple inheritance).",
                "c": "Interfaces can be instantiated directly; abstract classes cannot.",
                "d": "Abstract classes cannot have concrete method implementations.",
                "ans": "B",
                "exp": "Abstract classes can hold state (fields) and constructors and can have concrete methods. Interfaces represent pure capability contracts, and languages like Java/C# allow a class to implement multiple interfaces."
            },
            {
                "cat": "Object-Oriented Programming",
                "text": "What is the Singleton design pattern and what is a common pitfall when implementing it?",
                "diff": "Medium",
                "a": "A pattern that creates a pool of 10 objects; pitfall is array bound overflow.",
                "b": "A creational pattern that restricts class instantiation to a single instance; pitfall is improper thread-safety handling during double-checked locking.",
                "c": "A structural pattern that converts XML to JSON.",
                "d": "A behavioral pattern used only for database connections.",
                "ans": "B",
                "exp": "The Singleton pattern ensures only one instance of a class exists across the application runtime. Pitfalls include multithreading synchronization bugs during lazy initialization and difficulties with unit test mocking."
            },
            {
                "cat": "Object-Oriented Programming",
                "text": "What is the difference between Composition and Inheritance?",
                "diff": "Medium",
                "a": "Inheritance represents a 'has-a' relationship; Composition represents an 'is-a' relationship.",
                "b": "Composition represents a 'has-a' relationship (favor composition over inheritance for looser coupling); Inheritance represents an 'is-a' hierarchy.",
                "c": "Composition requires abstract virtual classes.",
                "d": "Inheritance cannot reuse existing class methods.",
                "ans": "B",
                "exp": "'Composition over inheritance' is a core OOP guideline. Inheritance binds classes closely ('is-a' relationship, white-box reuse), whereas Composition combines loosely coupled objects ('has-a' relationship, black-box reuse)."
            },
            {
                "cat": "Object-Oriented Programming",
                "text": "What is the Factory Method design pattern?",
                "diff": "Medium",
                "a": "A pattern that encapsulates object creation by allowing subclasses to decide which class to instantiate.",
                "b": "A pattern that executes SQL queries concurrently.",
                "c": "A structural pattern used to wrap existing legacy APIs.",
                "d": "A pattern that logs errors to disk.",
                "ans": "A",
                "exp": "The Factory Method pattern defines an interface for creating an object, but lets subclasses alter the type of objects that will be created, decoupling client code from concrete implementations."
            },

            # Data Structures and Algorithms
            {
                "cat": "Data Structures and Algorithms",
                "text": "What is the worst-case and average-case time complexity of QuickSort?",
                "diff": "Easy",
                "a": "Worst: O(n log n), Average: O(n^2)",
                "b": "Worst: O(n^2), Average: O(n log n)",
                "c": "Worst: O(n), Average: O(1)",
                "d": "Worst: O(n log n), Average: O(n log n)",
                "ans": "B",
                "exp": "QuickSort partitions around a pivot. On average it divides arrays evenly, achieving O(n log n). If unbalanced pivots are picked repeatedly (e.g. sorted array with last element pivot), worst case degrades to O(n^2)."
            },
            {
                "cat": "Data Structures and Algorithms",
                "text": "How do you detect a cycle in a singly linked list with O(1) auxiliary space?",
                "diff": "Medium",
                "a": "Store all visited node addresses in a Hash Set.",
                "b": "Floyd's Cycle-Finding Algorithm (Tortoise and Hare pointer approach).",
                "c": "Sort the linked list using Merge Sort.",
                "d": "Count the number of nodes using recursion.",
                "ans": "B",
                "exp": "Floyd's algorithm uses two pointers moving at different speeds: slow (1 step) and fast (2 steps). If a cycle exists, they will inevitably meet inside the loop in O(n) time and O(1) auxiliary space."
            },
            {
                "cat": "Data Structures and Algorithms",
                "text": "What is the time complexity of searching, inserting, and deleting in a balanced Binary Search Tree (such as an AVL or Red-Black Tree)?",
                "diff": "Easy",
                "a": "O(1)",
                "b": "O(log n)",
                "c": "O(n)",
                "d": "O(n log n)",
                "ans": "B",
                "exp": "Self-balancing binary search trees maintain a maximum height of O(log n), guaranteeing O(log n) time complexity for search, insert, and delete operations."
            },
            {
                "cat": "Data Structures and Algorithms",
                "text": "Which data structure is primarily used to implement Breadth-First Search (BFS) on a graph?",
                "diff": "Easy",
                "a": "Stack",
                "b": "Queue",
                "c": "Binary Heap",
                "d": "Hash Map",
                "ans": "B",
                "exp": "Breadth-First Search processes vertices level by level in First-In-First-Out order, making a Queue the standard data structure. (DFS uses a Stack or call stack)."
            },
            {
                "cat": "Data Structures and Algorithms",
                "text": "What is the main difference between Dynamic Programming and Divide & Conquer?",
                "diff": "Medium",
                "a": "Divide & Conquer handles overlapping subproblems; Dynamic Programming solves independent subproblems.",
                "b": "Dynamic Programming is applied to problems with overlapping subproblems and optimal substructure (caching subproblem solutions); Divide & Conquer solves non-overlapping independent subproblems.",
                "c": "Dynamic Programming cannot be implemented with recursion.",
                "d": "Divide & Conquer always uses memoization tables.",
                "ans": "B",
                "exp": "Dynamic Programming solves subproblems and stores their results (memoization/tabulation) because subproblems overlap (e.g. Fibonacci, 0/1 Knapsack). Divide & Conquer divides into independent subproblems (e.g. MergeSort)."
            },
            {
                "cat": "Data Structures and Algorithms",
                "text": "What is the minimum number of queues required to implement a Stack data structure?",
                "diff": "Medium",
                "a": "1",
                "b": "2",
                "c": "3",
                "d": "4",
                "ans": "B",
                "exp": "A LIFO stack can be simulated using two FIFO queues by pushing new elements into an empty queue and transferring all older elements behind it."
            },
            {
                "cat": "Data Structures and Algorithms",
                "text": "What is the space complexity of Depth First Search (DFS) on a tree of height h?",
                "diff": "Medium",
                "a": "O(1)",
                "b": "O(h)",
                "c": "O(2^h)",
                "d": "O(h^2)",
                "ans": "B",
                "exp": "The space complexity of DFS is governed by the maximum depth of the recursion stack, which equals the height of the tree O(h)."
            },

            # Aptitude
            {
                "cat": "Aptitude",
                "text": "A train 240 m long passes a pole in 24 seconds. How long will it take to pass a platform 650 m long?",
                "diff": "Medium",
                "a": "65 seconds",
                "b": "89 seconds",
                "c": "100 seconds",
                "d": "75 seconds",
                "ans": "B",
                "exp": "Speed of train = 240m / 24s = 10 m/s. Total distance to pass platform = 240m + 650m = 890m. Time taken = 890m / 10 m/s = 89 seconds."
            },
            {
                "cat": "Aptitude",
                "text": "A can do a work in 15 days and B in 20 days. If they work on it together for 4 days, then the fraction of the work that is left is:",
                "diff": "Medium",
                "a": "7/15",
                "b": "8/15",
                "c": "1/2",
                "d": "1/4",
                "ans": "B",
                "exp": "A's 1-day work = 1/15, B's 1-day work = 1/20. Together in 1 day = (1/15 + 1/20) = 7/60. Work done in 4 days = 4 * (7/60) = 28/60 = 7/15. Work left = 1 - 7/15 = 8/15."
            },
            {
                "cat": "Aptitude",
                "text": "If a merchant sells an item at Rs. 960 and incurs a loss of 4%, at what price should he sell it to gain 10%?",
                "diff": "Easy",
                "a": "Rs. 1000",
                "b": "Rs. 1100",
                "c": "Rs. 1050",
                "d": "Rs. 1150",
                "ans": "B",
                "exp": "Loss = 4%, so SP = 96% of CP. 0.96 * CP = 960 => CP = 1000. To gain 10%, new SP = 1.10 * 1000 = Rs. 1100."
            },
            {
                "cat": "Aptitude",
                "text": "Find the missing number in the series: 3, 7, 15, 31, 63, ?",
                "diff": "Easy",
                "a": "95",
                "b": "111",
                "c": "127",
                "d": "128",
                "ans": "C",
                "exp": "The pattern is (x * 2) + 1: 3*2+1=7, 7*2+1=15, 15*2+1=31, 31*2+1=63, 63*2+1 = 127."
            },
            {
                "cat": "Aptitude",
                "text": "In how many different ways can the letters of the word 'LEADER' be arranged?",
                "diff": "Medium",
                "a": "720",
                "b": "360",
                "c": "120",
                "d": "180",
                "ans": "B",
                "exp": "'LEADER' has 6 letters where 'E' appears twice. Total arrangements = 6! / 2! = 720 / 2 = 360 ways."
            },
            {
                "cat": "Aptitude",
                "text": "A sum of money at simple interest doubles in 8 years. In how many years will it become 4 times of itself at the same rate?",
                "diff": "Medium",
                "a": "16 years",
                "b": "24 years",
                "c": "32 years",
                "d": "20 years",
                "ans": "B",
                "exp": "Doubling means interest = P in 8 years. Rate = 100/8 = 12.5%. For sum to quadruple, interest = 3P. Time = (3P * 100) / (P * 12.5) = 24 years."
            },
            {
                "cat": "Aptitude",
                "text": "A clock shows 3:30. What is the angle between the hour hand and the minute hand?",
                "diff": "Medium",
                "a": "60 degrees",
                "b": "75 degrees",
                "c": "90 degrees",
                "d": "85 degrees",
                "ans": "B",
                "exp": "Angle = |30*H - (11/2)*M| = |30*3 - (11/2)*30| = |90 - 165| = 75 degrees."
            },

            # HR Interview
            {
                "cat": "HR Interview",
                "text": "What does the STAR interview technique stand for when answering behavioral questions?",
                "diff": "Easy",
                "a": "Strength, Talent, Ability, Result",
                "b": "Situation, Task, Action, Result",
                "c": "Strategy, Timeline, Assignment, Review",
                "d": "Skills, Technical knowledge, Achievements, Recommendations",
                "ans": "B",
                "exp": "The STAR method structures answers to behavioral questions: Situation (context), Task (objective), Action (specific steps you took), and Result (measurable outcome)."
            },
            {
                "cat": "HR Interview",
                "text": "When an interviewer asks 'What is your greatest weakness?', what is the most professional response strategy?",
                "diff": "Easy",
                "a": "Say you have no weaknesses and work perfectly.",
                "b": "Acknowledge a genuine professional area of improvement and explain the concrete proactive steps you are taking to overcome it.",
                "c": "Disclose a critical technical flaw that directly incapacitates the core job requirement.",
                "d": "Disguise a disguised humblebrag like 'I work too hard and care too much'.",
                "ans": "B",
                "exp": "Interviewers look for self-awareness and continuous learning. State a real non-fatal weakness (e.g. public speaking or delegating) followed by concrete actions taken to improve."
            },
            {
                "cat": "HR Interview",
                "text": "Why do interviewers ask: 'Why do you want to join our company?'",
                "diff": "Easy",
                "a": "To test if you memorized the salary range.",
                "b": "To assess whether you researched the company's culture, mission, and products, and if your career goals align with their vision.",
                "c": "To find out how many other companies rejected you.",
                "d": "To test your knowledge of stock prices.",
                "ans": "B",
                "exp": "This question tests your enthusiasm, preparation, and cultural alignment. A great answer connects specific company projects or values with your personal skills and passions."
            },
            {
                "cat": "HR Interview",
                "text": "How should a candidate handle a situation where they do not know the answer to a technical question during an interview?",
                "diff": "Easy",
                "a": "Guess randomly and pretend to be completely certain.",
                "b": "Honoring honesty: Calmly acknowledge you are unfamiliar with the specific concept, explain how you would logically reason through it or look it up, and ask for a hint.",
                "c": "Argue with the interviewer that the question is invalid.",
                "d": "Remain silent until the interviewer moves to the next question.",
                "ans": "B",
                "exp": "Integrity and problem-solving mindset are critical. Admitting you don't know while articulating your thought process shows confidence and coachability."
            },
            {
                "cat": "HR Interview",
                "text": "At the end of an interview, when asked 'Do you have any questions for us?', what should a candidate do?",
                "diff": "Easy",
                "a": "Say 'No, everything was covered' to finish early.",
                "b": "Ask thoughtful questions about engineering culture, team workflows, tech stack evolution, or current challenges.",
                "c": "Immediately ask how much paid time off is provided.",
                "d": "Ask whether you passed the interview right then.",
                "ans": "B",
                "exp": "Asking meaningful questions displays curiosity, preparation, and genuine interest in the team and role."
            },
            {
                "cat": "HR Interview",
                "text": "When asked to describe a conflict with a teammate, what is the key quality interviewers evaluate?",
                "diff": "Medium",
                "a": "Whether you proved the teammate wrong and won the dispute.",
                "b": "Professionalism, active listening, empathy, and your ability to reach a collaborative, productive resolution focused on project success.",
                "c": "How quickly you escalated the conflict to HR or senior management.",
                "d": "Whether you avoided speaking to the teammate afterward.",
                "ans": "B",
                "exp": "Conflict is inevitable in teamwork. The goal is to show maturity, emotional intelligence, open communication, and alignment toward team objectives."
            },
            {
                "cat": "HR Interview",
                "text": "What is the best way to answer: 'Where do you see yourself in 5 years?'",
                "diff": "Medium",
                "a": "Express a clear trajectory of growing technical expertise, taking on greater architectural/team ownership, and contributing meaningfully to company goals.",
                "b": "Say you plan to start your own competing startup in two years.",
                "c": "Say 'I want to have your job' to sound ambitious.",
                "d": "Say you have no plans because the future is unpredictable.",
                "ans": "A",
                "exp": "Employers want to see commitment, realistic career ambitions, and a desire to grow your skills while providing value to the organization."
            }
        ]

        created_questions = []
        for qd in raw_questions:
            cat_obj = cats_map.get(qd['cat'])
            if not cat_obj:
                continue
            q = Question(
                category_id=cat_obj.id,
                question_text=qd['text'],
                difficulty=qd['diff'],
                question_type="mcq",
                option_a=qd['a'],
                option_b=qd['b'],
                option_c=qd['c'],
                option_d=qd['d'],
                correct_answer=qd['ans'],
                explanation=qd['exp'],
                created_at=datetime.utcnow() - timedelta(days=15)
            )
            db.session.add(q)
            db.session.flush()
            created_questions.append(q)

        db.session.commit()
        print(f"   Successfully added {len(created_questions)} interview questions.")

        # 4. MOCK TESTS (5 Timed Tests)
        print("   Creating 5 Timed Mock Tests with Question Associations...")
        mock_tests_info = [
            {
                "title": "Full Stack Campus Placement Mock Test",
                "description": "Comprehensive timed evaluation simulating top tier campus placement screening tests across Java, Python, DBMS, OS, Networks, and Aptitude.",
                "cat": "Data Structures and Algorithms",
                "duration": 30,
                "passing": 60.0,
                "difficulty": "Medium",
                "q_count": 15
            },
            {
                "title": "Core Computer Science Fundamentals Assessment",
                "description": "Essential diagnostic test covering Operating Systems, Database Management Systems, and Computer Networks.",
                "cat": "Operating Systems",
                "duration": 25,
                "passing": 65.0,
                "difficulty": "Medium",
                "q_count": 12
            },
            {
                "title": "Data Structures & OOP Mastery Sprint",
                "description": "Rigorous timed assessment evaluating algorithmic complexity, object-oriented concepts, and core data structure operations.",
                "cat": "Object-Oriented Programming",
                "duration": 20,
                "passing": 70.0,
                "difficulty": "Hard",
                "q_count": 10
            },
            {
                "title": "Python & Java Programming Proficiency Test",
                "description": "In-depth test on modern Python and Java runtime mechanics, memory models, collections, and multi-threading.",
                "cat": "Python",
                "duration": 20,
                "passing": 60.0,
                "difficulty": "Medium",
                "q_count": 10
            },
            {
                "title": "Quantitative & Logical Aptitude Qualifier",
                "description": "Speed and accuracy assessment covering numbers, percentages, work & time, permutations, series, and logical deduction.",
                "cat": "Aptitude",
                "duration": 15,
                "passing": 60.0,
                "difficulty": "Easy",
                "q_count": 7
            }
        ]

        created_tests = []
        for t_info in mock_tests_info:
            c_obj = cats_map.get(t_info['cat'])
            mt = MockTest(
                title=t_info['title'],
                description=t_info['description'],
                category_id=c_obj.id if c_obj else None,
                duration_minutes=t_info['duration'],
                passing_percentage=t_info['passing'],
                difficulty=t_info['difficulty'],
                is_published=True,
                total_marks=t_info['q_count'],
                created_at=datetime.utcnow() - timedelta(days=10)
            )
            db.session.add(mt)
            db.session.flush()

            # Associate questions
            if t_info['title'] == "Full Stack Campus Placement Mock Test":
                assigned_qs = created_questions[:15]
            elif t_info['title'] == "Core Computer Science Fundamentals Assessment":
                assigned_qs = [q for q in created_questions if q.category.name in ["Operating Systems", "DBMS", "Computer Networks"]][:12]
            elif t_info['title'] == "Data Structures & OOP Mastery Sprint":
                assigned_qs = [q for q in created_questions if q.category.name in ["Data Structures and Algorithms", "Object-Oriented Programming"]][:10]
            elif t_info['title'] == "Python & Java Programming Proficiency Test":
                assigned_qs = [q for q in created_questions if q.category.name in ["Python", "Java"]][:10]
            else:
                assigned_qs = [q for q in created_questions if q.category.name == "Aptitude"][:7]

            mt.total_marks = len(assigned_qs)
            for q_item in assigned_qs:
                tq = TestQuestion(test_id=mt.id, question_id=q_item.id, marks=1)
                db.session.add(tq)

            created_tests.append(mt)

        db.session.commit()
        print(f"   Successfully added {len(created_tests)} mock tests.")

        # 5. CODING PROBLEMS (15 Beginner-Friendly Programming Problems)
        print("   Creating 15 Interactive Coding Problems...")
        coding_problems_data = [
            {
                "title": "Find the Largest Element in an Array",
                "slug": "find-largest-element-array",
                "difficulty": "Easy",
                "category": "Arrays",
                "description": "Given an integer array, write a program to find and print the maximum (largest) element in the array.",
                "input_format": "The first line contains an integer N (the number of elements). The second line contains N space-separated integers.",
                "output_format": "Print the maximum integer in the array.",
                "sample_input": "5\n3 7 2 9 4",
                "sample_output": "9",
                "constraints": "1 <= N <= 10^5\n-10^9 <= A[i] <= 10^9",
                "hints": "Initialize a variable `max_val` to negative infinity or the first element, then loop through all elements updating `max_val` whenever an element is larger.",
                "solution_explanation": "We read N and the array of integers, initialize max_val = arr[0], and iterate through each number in arr updating max_val = max(max_val, num). Finally, print(max_val).",
                "starter_code": "import sys\n\ndef main():\n    lines = sys.stdin.read().split()\n    if not lines:\n        return\n    n = int(lines[0])\n    arr = [int(x) for x in lines[1:n+1]]\n    \n    # Your logic here:\n    max_val = max(arr)\n    print(max_val)\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "5\n3 7 2 9 4", "expected": "9", "is_hidden": False},
                    {"input": "4\n-10 -5 -20 -1", "expected": "-1", "is_hidden": False},
                    {"input": "1\n42", "expected": "42", "is_hidden": True},
                    {"input": "6\n100 200 50 400 300 250", "expected": "400", "is_hidden": True}
                ]
            },
            {
                "title": "Reverse a String",
                "slug": "reverse-a-string",
                "difficulty": "Easy",
                "category": "Strings",
                "description": "Given a string S, reverse the string and print the reversed output.",
                "input_format": "A single line containing the string S.",
                "output_format": "Print the reversed string.",
                "sample_input": "hello",
                "sample_output": "olleh",
                "constraints": "1 <= len(S) <= 1000",
                "hints": "You can use two pointers, a stack, or Python slicing `S[::-1]`.",
                "solution_explanation": "Read string S, strip trailing newlines, and print the reversed string using slicing `s[::-1]` or `.join(reversed(s))`.",
                "starter_code": "import sys\n\ndef main():\n    s = sys.stdin.read().strip()\n    # Your logic here:\n    print(s[::-1])\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "hello", "expected": "olleh", "is_hidden": False},
                    {"input": "algorithm", "expected": "mhtirogla", "is_hidden": False},
                    {"input": "racecar", "expected": "racecar", "is_hidden": True},
                    {"input": "OpenAI", "expected": "IAnepO", "is_hidden": True}
                ]
            },
            {
                "title": "Check Whether a Number is Prime",
                "slug": "check-prime-number",
                "difficulty": "Easy",
                "category": "Math",
                "description": "Given an integer N, determine whether N is a prime number. Print 'YES' if prime, otherwise 'NO'.",
                "input_format": "A single integer N.",
                "output_format": "Print 'YES' if N is prime, otherwise 'NO'.",
                "sample_input": "29",
                "sample_output": "YES",
                "constraints": "1 <= N <= 10^9",
                "hints": "Numbers less than or equal to 1 are not prime. For N > 1, check divisibility up to integer square root of N.",
                "solution_explanation": "If N <= 1, False. If N in (2, 3), True. Check if divisible by 2 or 3, then check 6k +/- 1 up to sqrt(N).",
                "starter_code": "import sys\n\ndef is_prime(n):\n    if n <= 1:\n        return False\n    if n <= 3:\n        return True\n    if n % 2 == 0 or n % 3 == 0:\n        return False\n    i = 5\n    while i * i <= n:\n        if n % i == 0 or n % (i + 2) == 0:\n            return False\n        i += 6\n    return True\n\ndef main():\n    val = sys.stdin.read().strip()\n    if val:\n        n = int(val)\n        print(\"YES\" if is_prime(n) else \"NO\")\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "29", "expected": "YES", "is_hidden": False},
                    {"input": "15", "expected": "NO", "is_hidden": False},
                    {"input": "1", "expected": "NO", "is_hidden": True},
                    {"input": "97", "expected": "YES", "is_hidden": True}
                ]
            },
            {
                "title": "Check Whether a String is a Palindrome",
                "slug": "check-palindrome-string",
                "difficulty": "Easy",
                "category": "Strings",
                "description": "Given a string S, check whether it is a palindrome (reads identically forwards and backwards). Print 'YES' or 'NO'.",
                "input_format": "A single line containing string S.",
                "output_format": "Print 'YES' if S is a palindrome, otherwise 'NO'.",
                "sample_input": "madam",
                "sample_output": "YES",
                "constraints": "1 <= len(S) <= 10^5",
                "hints": "Compare the string with its reverse, ignoring whitespace and case if required, or simply check S == S[::-1].",
                "solution_explanation": "Read string S, compare S.lower() with S.lower()[::-1]. If equal, print 'YES', else 'NO'.",
                "starter_code": "import sys\n\ndef main():\n    s = sys.stdin.read().strip()\n    # Your logic here:\n    if s.lower() == s.lower()[::-1]:\n        print(\"YES\")\n    else:\n        print(\"NO\")\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "madam", "expected": "YES", "is_hidden": False},
                    {"input": "smartprep", "expected": "NO", "is_hidden": False},
                    {"input": "noon", "expected": "YES", "is_hidden": True},
                    {"input": "developer", "expected": "NO", "is_hidden": True}
                ]
            },
            {
                "title": "Calculate Factorial",
                "slug": "calculate-factorial",
                "difficulty": "Easy",
                "category": "Math",
                "description": "Given a non-negative integer N, calculate its factorial (N!). 0! = 1.",
                "input_format": "A single non-negative integer N.",
                "output_format": "Print the value of N!.",
                "sample_input": "5",
                "sample_output": "120",
                "constraints": "0 <= N <= 20",
                "hints": "Use an iterative loop from 1 to N multiplying into an accumulator initialized to 1.",
                "solution_explanation": "Factorial of N is the product of all positive integers less than or equal to N. For 0, return 1.",
                "starter_code": "import sys\n\ndef main():\n    line = sys.stdin.read().strip()\n    if line:\n        n = int(line)\n        ans = 1\n        for i in range(1, n + 1):\n            ans *= i\n        print(ans)\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "5", "expected": "120", "is_hidden": False},
                    {"input": "0", "expected": "1", "is_hidden": False},
                    {"input": "7", "expected": "5040", "is_hidden": True},
                    {"input": "10", "expected": "3628800", "is_hidden": True}
                ]
            },
            {
                "title": "Generate Fibonacci Numbers",
                "slug": "generate-fibonacci-numbers",
                "difficulty": "Easy",
                "category": "Math",
                "description": "Given an integer N, print the first N Fibonacci numbers separated by a space. The sequence starts: 0 1 1 2 3...",
                "input_format": "A single integer N.",
                "output_format": "Print the first N Fibonacci numbers separated by space.",
                "sample_input": "7",
                "sample_output": "0 1 1 2 3 5 8",
                "constraints": "1 <= N <= 50",
                "hints": "Maintain two variables a = 0, b = 1 and in each step update (a, b) = (b, a + b).",
                "solution_explanation": "Initialize list fib = [0, 1]. For N == 1, print '0'. For N > 2, loop up to N appending sum of last two elements.",
                "starter_code": "import sys\n\ndef main():\n    line = sys.stdin.read().strip()\n    if not line:\n        return\n    n = int(line)\n    if n == 1:\n        print(\"0\")\n        return\n    fib = [0, 1]\n    while len(fib) < n:\n        fib.append(fib[-1] + fib[-2])\n    print(\" \".join(map(str, fib[:n])))\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "7", "expected": "0 1 1 2 3 5 8", "is_hidden": False},
                    {"input": "1", "expected": "0", "is_hidden": False},
                    {"input": "5", "expected": "0 1 1 2 3", "is_hidden": True},
                    {"input": "10", "expected": "0 1 1 2 3 5 8 13 21 34", "is_hidden": True}
                ]
            },
            {
                "title": "Find the Sum of Array Elements",
                "slug": "sum-of-array-elements",
                "difficulty": "Easy",
                "category": "Arrays",
                "description": "Given an array of N integers, find and print the sum of all elements.",
                "input_format": "First line contains N. Second line contains N integers.",
                "output_format": "Print the integer sum.",
                "sample_input": "4\n1 2 3 4",
                "sample_output": "10",
                "constraints": "1 <= N <= 10^5",
                "hints": "Use Python's built-in sum() or an iterative accumulator loop.",
                "solution_explanation": "Read integers and calculate sum(arr).",
                "starter_code": "import sys\n\ndef main():\n    parts = sys.stdin.read().split()\n    if not parts:\n        return\n    n = int(parts[0])\n    arr = [int(x) for x in parts[1:n+1]]\n    print(sum(arr))\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "4\n1 2 3 4", "expected": "10", "is_hidden": False},
                    {"input": "3\n-5 5 10", "expected": "10", "is_hidden": False},
                    {"input": "5\n10 20 30 40 50", "expected": "150", "is_hidden": True}
                ]
            },
            {
                "title": "Count Vowels in a String",
                "slug": "count-vowels-in-string",
                "difficulty": "Easy",
                "category": "Strings",
                "description": "Given a string S, count the total number of vowels ('a', 'e', 'i', 'o', 'u', case-insensitive).",
                "input_format": "A single line string S.",
                "output_format": "Print the number of vowels.",
                "sample_input": "Education",
                "sample_output": "5",
                "constraints": "1 <= len(S) <= 10^5",
                "hints": "Define a set of vowels `vowels = set('aeiouAEIOU')` and count matching characters in S.",
                "solution_explanation": "Iterate over each character of S, check if char in 'aeiouAEIOU', and sum matches.",
                "starter_code": "import sys\n\ndef main():\n    s = sys.stdin.read().strip()\n    vowels = set('aeiouAEIOU')\n    count = sum(1 for c in s if c in vowels)\n    print(count)\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "Education", "expected": "5", "is_hidden": False},
                    {"input": "xyz", "expected": "0", "is_hidden": False},
                    {"input": "Smart Interview Platform", "expected": "7", "is_hidden": True}
                ]
            },
            {
                "title": "Sort an Array",
                "slug": "sort-an-array",
                "difficulty": "Easy",
                "category": "Arrays",
                "description": "Given an array of N integers, sort the elements in ascending order and print them separated by spaces.",
                "input_format": "First line contains N. Second line contains N integers.",
                "output_format": "Print the sorted array separated by spaces.",
                "sample_input": "5\n4 2 1 5 3",
                "sample_output": "1 2 3 4 5",
                "constraints": "1 <= N <= 10^5",
                "hints": "Use Python's TimSort via `sorted()` or `.sort()`.",
                "solution_explanation": "Read integers into a list, call arr.sort(), and join elements with spaces.",
                "starter_code": "import sys\n\ndef main():\n    parts = sys.stdin.read().split()\n    if not parts:\n        return\n    n = int(parts[0])\n    arr = [int(x) for x in parts[1:n+1]]\n    arr.sort()\n    print(\" \".join(map(str, arr)))\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "5\n4 2 1 5 3", "expected": "1 2 3 4 5", "is_hidden": False},
                    {"input": "3\n10 -2 0", "expected": "-2 0 10", "is_hidden": False},
                    {"input": "6\n9 8 7 6 5 4", "expected": "4 5 6 7 8 9", "is_hidden": True}
                ]
            },
            {
                "title": "Find Duplicate Elements",
                "slug": "find-duplicate-elements",
                "difficulty": "Medium",
                "category": "Arrays",
                "description": "Given an array of N integers, print all numbers that appear more than once, sorted in ascending order. If no duplicates exist, print -1.",
                "input_format": "First line contains N. Second line contains N space-separated integers.",
                "output_format": "Print duplicate elements sorted, separated by spaces. Print -1 if none.",
                "sample_input": "6\n1 2 3 2 4 1",
                "sample_output": "1 2",
                "constraints": "1 <= N <= 10^5",
                "hints": "Use a hash map or frequency dictionary to count occurrences, then collect keys with count > 1 and sort.",
                "solution_explanation": "Count frequencies with collections.Counter, filter keys where count > 1, sort and print.",
                "starter_code": "import sys\nfrom collections import Counter\n\ndef main():\n    parts = sys.stdin.read().split()\n    if not parts:\n        return\n    n = int(parts[0])\n    arr = [int(x) for x in parts[1:n+1]]\n    counts = Counter(arr)\n    dups = sorted([k for k, v in counts.items() if v > 1])\n    if dups:\n        print(\" \".join(map(str, dups)))\n    else:\n        print(\"-1\")\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "6\n1 2 3 2 4 1", "expected": "1 2", "is_hidden": False},
                    {"input": "4\n1 2 3 4", "expected": "-1", "is_hidden": False},
                    {"input": "5\n5 5 5 5 5", "expected": "5", "is_hidden": True}
                ]
            },
            {
                "title": "Check for an Armstrong Number",
                "slug": "check-armstrong-number",
                "difficulty": "Easy",
                "category": "Math",
                "description": "An Armstrong number of order d is a number equal to the sum of its digits each raised to power d. Print 'YES' if N is Armstrong, otherwise 'NO'.",
                "input_format": "A single integer N.",
                "output_format": "Print 'YES' or 'NO'.",
                "sample_input": "153",
                "sample_output": "YES",
                "constraints": "1 <= N <= 10^9",
                "hints": "For 153, order d = 3. 1^3 + 5^3 + 3^3 = 1 + 125 + 27 = 153.",
                "solution_explanation": "Extract digits as string, let d = len(digits). Compute sum of int(digit)^d and compare with original integer.",
                "starter_code": "import sys\n\ndef main():\n    line = sys.stdin.read().strip()\n    if not line:\n        return\n    num_str = line\n    d = len(num_str)\n    total = sum(int(ch) ** d for ch in num_str)\n    if total == int(num_str):\n        print(\"YES\")\n    else:\n        print(\"NO\")\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "153", "expected": "YES", "is_hidden": False},
                    {"input": "120", "expected": "NO", "is_hidden": False},
                    {"input": "370", "expected": "YES", "is_hidden": True},
                    {"input": "9474", "expected": "YES", "is_hidden": True}
                ]
            },
            {
                "title": "Find the Second-Largest Element",
                "slug": "find-second-largest-element",
                "difficulty": "Medium",
                "category": "Arrays",
                "description": "Given an array of N integers, find the distinct second-largest element. If no distinct second-largest exists, print -1.",
                "input_format": "First line contains N. Second line contains N integers.",
                "output_format": "Print the second-largest distinct integer, or -1.",
                "sample_input": "5\n12 35 1 10 34",
                "sample_output": "34",
                "constraints": "2 <= N <= 10^5",
                "hints": "Remove duplicates by converting to a set, sort descending, and check if length >= 2.",
                "solution_explanation": "Convert array to set to eliminate duplicates. If len(unique) < 2, return -1. Otherwise sort and pick the second element.",
                "starter_code": "import sys\n\ndef main():\n    parts = sys.stdin.read().split()\n    if not parts:\n        return\n    n = int(parts[0])\n    arr = [int(x) for x in parts[1:n+1]]\n    distinct = sorted(list(set(arr)), reverse=True)\n    if len(distinct) < 2:\n        print(\"-1\")\n    else:\n        print(distinct[1])\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "5\n12 35 1 10 34", "expected": "34", "is_hidden": False},
                    {"input": "3\n10 10 10", "expected": "-1", "is_hidden": False},
                    {"input": "4\n-1 -5 -2 -10", "expected": "-2", "is_hidden": True}
                ]
            },
            {
                "title": "Count Character Frequencies",
                "slug": "count-character-frequencies",
                "difficulty": "Easy",
                "category": "Strings",
                "description": "Given a lowercase string S, count the frequency of each character and print each character and its count separated by colon, sorted alphabetically.",
                "input_format": "A single line containing string S.",
                "output_format": "Print each character and its frequency formatted as 'char:count' separated by spaces.",
                "sample_input": "banana",
                "sample_output": "a:3 b:1 n:2",
                "constraints": "1 <= len(S) <= 10^5",
                "hints": "Count occurrences using a dictionary, sort the keys alphabetically, and format output.",
                "solution_explanation": "Use collections.Counter or a dict, sort keys, and join formatted strings.",
                "starter_code": "import sys\nfrom collections import Counter\n\ndef main():\n    s = sys.stdin.read().strip()\n    counts = Counter(s)\n    sorted_items = sorted(counts.items())\n    print(\" \".join(f\"{k}:{v}\" for k, v in sorted_items))\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "banana", "expected": "a:3 b:1 n:2", "is_hidden": False},
                    {"input": "hello", "expected": "e:1 h:1 l:2 o:1", "is_hidden": False},
                    {"input": "a", "expected": "a:1", "is_hidden": True}
                ]
            },
            {
                "title": "Remove Duplicates from an Array",
                "slug": "remove-duplicates-from-array",
                "difficulty": "Easy",
                "category": "Arrays",
                "description": "Given an array of N integers, remove all duplicate occurrences while maintaining their original relative order. Print the unique elements separated by space.",
                "input_format": "First line contains N. Second line contains N integers.",
                "output_format": "Print unique elements preserving relative order, separated by space.",
                "sample_input": "6\n1 2 2 3 4 4",
                "sample_output": "1 2 3 4",
                "constraints": "1 <= N <= 10^5",
                "hints": "Maintain a `seen` set while iterating through the array to filter previously encountered numbers.",
                "solution_explanation": "Iterate through elements; if element not in seen set, add to seen and result list.",
                "starter_code": "import sys\n\ndef main():\n    parts = sys.stdin.read().split()\n    if not parts:\n        return\n    n = int(parts[0])\n    arr = [int(x) for x in parts[1:n+1]]\n    seen = set()\n    res = []\n    for num in arr:\n        if num not in seen:\n            seen.add(num)\n            res.append(num)\n    print(\" \".join(map(str, res)))\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "6\n1 2 2 3 4 4", "expected": "1 2 3 4", "is_hidden": False},
                    {"input": "5\n5 1 2 1 5", "expected": "5 1 2", "is_hidden": False},
                    {"input": "4\n10 20 30 40", "expected": "10 20 30 40", "is_hidden": True}
                ]
            },
            {
                "title": "Find the Missing Number in a Sequence",
                "slug": "find-missing-number-sequence",
                "difficulty": "Easy",
                "category": "Math",
                "description": "Given an array containing N distinct numbers in the range [1, N+1], find the single number missing from the sequence.",
                "input_format": "First line contains N (size of array). Second line contains N space-separated integers.",
                "output_format": "Print the missing integer.",
                "sample_input": "4\n1 2 4 5",
                "sample_output": "3",
                "constraints": "1 <= N <= 10^5",
                "hints": "Calculate expected sum for numbers 1 to N+1 using formula: (N+1)*(N+2)//2 and subtract actual array sum.",
                "solution_explanation": "Total sum formula S = (N+1)*(N+2)//2. Missing number = S - sum(arr).",
                "starter_code": "import sys\n\ndef main():\n    parts = sys.stdin.read().split()\n    if not parts:\n        return\n    n = int(parts[0])\n    arr = [int(x) for x in parts[1:n+1]]\n    expected = ((n + 1) * (n + 2)) // 2\n    print(expected - sum(arr))\n\nif __name__ == '__main__':\n    main()\n",
                "test_cases": [
                    {"input": "4\n1 2 4 5", "expected": "3", "is_hidden": False},
                    {"input": "2\n2 3", "expected": "1", "is_hidden": False},
                    {"input": "5\n1 2 3 4 5", "expected": "6", "is_hidden": True}
                ]
            }
        ]

        created_problems = []
        for cp in coding_problems_data:
            prob = CodingProblem(
                title=cp['title'],
                slug=cp['slug'],
                difficulty=cp['difficulty'],
                category=cp['category'],
                description=cp['description'],
                input_format=cp['input_format'],
                output_format=cp['output_format'],
                sample_input=cp['sample_input'],
                sample_output=cp['sample_output'],
                constraints=cp['constraints'],
                hints=cp['hints'],
                solution_explanation=cp['solution_explanation'],
                starter_code=cp['starter_code'],
                test_cases_json=json.dumps(cp['test_cases']),
                created_at=datetime.utcnow() - timedelta(days=20)
            )
            db.session.add(prob)
            db.session.flush()
            created_problems.append(prob)

        db.session.commit()
        print(f"   Successfully added {len(created_problems)} coding problems.")

        # 6. HR INTERVIEW QUESTIONS (20 Curated Questions with STAR Framework Guidance)
        print("   Creating 20 Curated HR Interview Questions...")
        hr_questions_data = [
            {
                "text": "Tell me about yourself.",
                "cat": "Introduction & Background",
                "tips": "Follow the Present-Past-Future model: 1. Present role and key technical interests, 2. Past relevant academic/project achievements, 3. Future aspirations and why you're excited for this role.",
                "example": "I am a final-year Computer Science student passionate about full-stack engineering and distributed systems. Recently, I built an end-to-end interview preparation platform using Python and Flask, improving assessment workflows for my peers. Previously, I led our college coding club where I mentored junior developers in DSA. I am eager to apply my software engineering skills and problem-solving mindset to contribute directly to high-impact products at your company.",
                "star": "Present: Current technical identity -> Past: 1-2 highlight projects with metrics -> Future: Genuine alignment with company."
            },
            {
                "text": "What are your greatest strengths?",
                "cat": "Strengths & Weaknesses",
                "tips": "Pick 2-3 genuine professional strengths directly relevant to software development (e.g., rapid learning, analytical problem-solving, collaborative communication) and back them with a concrete example.",
                "example": "My greatest strengths are rapid adaptability and root-cause problem solving. When building a team project, our initial database architecture experienced high latency. I independently analyzed the query execution plans, introduced indexing, and refactored table normalization, reducing query times by over 60%. I thrive on diagnosing technical roadblocks and collaborating with team members to deliver clean, scalable code.",
                "star": "Strength: Technical agility & problem solving -> Context: Database bottleneck -> Action: Query profiling & indexing -> Result: 60% latency reduction."
            },
            {
                "text": "What are your weaknesses and how are you addressing them?",
                "cat": "Strengths & Weaknesses",
                "tips": "Choose a real non-fatal weakness, show mature self-awareness, and detail the actionable systems or habits you have put in place to manage it.",
                "example": "Earlier in my engineering studies, I struggled with public speaking and presenting technical designs to large audiences. Recognizing that communication is as vital as coding, I pushed myself out of my comfort zone by volunteering to deliver sprint demos and leading technical workshops for juniors. While I still get occasional butterflies, structured rehearsal and slide outlines now help me communicate technical concepts confidently.",
                "star": "Weakness: Presentation anxiety -> Action: Volunteered for demos and peer workshops -> Outcome: Confident technical communicator."
            },
            {
                "text": "Why should we hire you over other candidates?",
                "cat": "Company & Career Goals",
                "tips": "Differentiate yourself through your blend of technical competence, hunger to learn, teamwork attitude, and alignment with their specific product mission.",
                "example": "You should hire me because I combine strong core software engineering fundamentals with a proactive builder mentality. Beyond coursework, I build functional applications, contribute to open discussions, and possess strong self-motivation. I don't just write code; I seek to understand user needs and architectural tradeoffs, making me someone who will onboard quickly and deliver reliable value to your team.",
                "star": "Unique value: Solid CS fundamentals + proven builder mindset + fast onboarding capability."
            },
            {
                "text": "Why do you want to work for our company?",
                "cat": "Company & Career Goals",
                "tips": "Mention specific products, company initiatives, culture, or technical challenges that genuinely inspire you.",
                "example": "I have been following your engineering blogs on modern cloud architectures and developer tooling. Your commitment to high availability and fostering an engineering culture that encourages continuous experimentation aligns deeply with how I want to grow as an engineer. I want to work where quality code solves real-world customer problems at scale.",
                "star": "Show genuine research: Cite engineering blog/product -> Express cultural alignment -> State how your contribution fits."
            },
            {
                "text": "Where do you see yourself in five years?",
                "cat": "Company & Career Goals",
                "tips": "Show realistic ambition: mastering software development, gaining architectural depth, mentoring peers, and taking technical ownership.",
                "example": "In five years, I see myself as a seasoned software engineer who has developed deep domain expertise in designing resilient distributed systems. I want to take technical ownership of end-to-end features, mentor incoming junior engineers, and play a pivotal role in architectural decisions that drive product performance.",
                "star": "Year 1-2: Master tech stack & deliver -> Year 3-4: Feature ownership & mentoring -> Year 5: Architectural leadership."
            },
            {
                "text": "Describe a significant technical challenge you overcame.",
                "cat": "Behavioral & STAR",
                "tips": "Use the STAR method. Focus on your thought process, technical options evaluated, and final outcome.",
                "example": "Situation: During our microproject development, our code execution engine faced security and infinite-loop execution risks. Task: I was responsible for implementing a safe execution sandbox. Action: Rather than using unrestricted eval(), I designed a multi-layer isolation pipeline: AST parsing to reject dangerous module imports like os and subprocess, followed by isolated sub-processes with strict 3-second timeouts. Result: The engine successfully runs student code safely without freezing the server, passing all test cases.",
                "star": "Situation: Unsafe execution danger -> Task: Build sandbox -> Action: AST validation + timeout subprocesses -> Result: 100% safe execution."
            },
            {
                "text": "Tell me about a time you worked in a team and faced a disagreement.",
                "cat": "Behavioral & STAR",
                "tips": "Highlight empathy, data-driven reasoning, active listening, and putting the project first.",
                "example": "Situation: In our database design phase, my teammate wanted to store all user test attempts in a single denormalized JSON column, whereas I advocated for normalized relational tables. Task: We needed to decide quickly to avoid blocking backend development. Action: I listened carefully to his speed concerns, then benchmarked both approaches for our specific reporting queries. I demonstrated that normalized tables allowed fast SQL aggregation for progress analytics while keeping indexes lean. Result: We agreed on normalized tables, and our reporting queries executed in under 20ms.",
                "star": "Situation: Conflicting schema ideas -> Task: Resolve without friction -> Action: Benchmarked query performance together -> Result: Data-driven consensus."
            },
            {
                "text": "How do you handle working under high pressure or tight deadlines?",
                "cat": "Situational & Pressure Handling",
                "tips": "Demonstrate prioritization, emotional composure, breaking tasks into milestones, and transparent stakeholder communication.",
                "example": "When facing tight deadlines, I immediately pause and prioritize. I break requirements into must-haves versus nice-to-haves using MoSCoW prioritization. During our final academic evaluation sprint, we faced multiple deliverables. I created a Kanban board, focused on the critical path first, and maintained clear status updates with my teammates. By eliminating multitasking and focusing on sequential execution, we delivered our project ahead of schedule without bugs.",
                "star": "Strategy: Prioritize via MoSCoW -> Break down into Kanban cards -> Execute sequentially -> Maintain communication."
            },
            {
                "text": "Tell me about a time you made a mistake. How did you handle it?",
                "cat": "Behavioral & STAR",
                "tips": "Take full accountability without blaming others. Focus on immediate mitigation and long-term prevention.",
                "example": "Situation: During an early project demo, I pushed a database migration script directly without backing up our development seed data, which accidentally wiped our test records minutes before our review. Task: I needed to restore data immediately and prevent recurrence. Action: I owned the mistake, quickly re-ran our automated seed script to regenerate realistic records, and then added a confirmation check to our reset CLI. Result: The demo went smoothly, and our project now has safeguarded migration scripts.",
                "star": "Mistake: Accidental seed reset -> Ownership: No excuses -> Mitigation: Reseeded instantly -> Prevention: Added CLI guardrails."
            },
            {
                "text": "How do you stay updated with emerging technologies and tools?",
                "cat": "Introduction & Background",
                "tips": "Mention podcasts, newsletters, GitHub repositories, official documentation, and building personal side projects.",
                "example": "I stay updated through a mix of reading and active experimentation. I read Hacker News and engineering blogs from companies like Netflix, Uber, and Google. When an interesting framework or concept emerges, like WebSockets or containerization, I build small proof-of-concept projects to understand its practical tradeoffs beyond the marketing hype.",
                "star": "Source: Tech publications & blogs -> Practice: Proof-of-concept coding -> Evaluation: Practical tradeoff analysis."
            },
            {
                "text": "What kind of work environment allows you to do your best work?",
                "cat": "Company & Career Goals",
                "tips": "Describe a culture that values psychological safety, clear objectives, constructive feedback, and technical curiosity.",
                "example": "I thrive in an open, collaborative environment where team members share knowledge freely and hold high standards for code quality. I appreciate having clear goals and the autonomy to design solutions, coupled with constructive code reviews where constructive feedback helps everyone grow.",
                "star": "Values: Open feedback + high engineering standards + autonomy with accountability."
            },
            {
                "text": "How do you prioritize multiple competing tasks or assignments?",
                "cat": "Situational & Pressure Handling",
                "tips": "Mention tools like Eisenhower Matrix, impact vs effort, and communicating early if bandwidth is constrained.",
                "example": "I evaluate tasks by urgency and project impact using an Eisenhower matrix. High-impact tasks critical to system stability or blocking colleagues take precedence. If overlapping deadlines create genuine bottlenecks, I proactively communicate with leads to align on priority rather than silently letting deliverables slip.",
                "star": "Framework: Impact vs urgency matrix -> Communication: Early alignment on trade-offs."
            },
            {
                "text": "Describe a situation where you had to learn a technology very quickly.",
                "cat": "Behavioral & STAR",
                "tips": "Explain your structured learning methodology: official docs, minimal toy project, debugging, and production integration.",
                "example": "Situation: Our microproject required Chart.js dynamic visualizations, which I hadn't used before. Task: I needed to build responsive radar and line charts within 48 hours. Action: I immersed myself in the official Chart.js documentation, created a standalone HTML sandbox to test chart configurations, and connected it to our Flask JSON endpoints. Result: Delivered 4 interactive charts on schedule that render seamlessly across desktop and mobile.",
                "star": "Situation: 48-hour Chart.js requirement -> Action: Docs + prototype sandbox + API integration -> Result: Flawless dynamic dashboard."
            },
            {
                "text": "How do you handle constructive criticism from peers or senior engineers?",
                "cat": "Strengths & Weaknesses",
                "tips": "Show that you separate your ego from your code and welcome code reviews as growth opportunities.",
                "example": "I view code reviews and constructive criticism as one of the fastest ways to grow as an engineer. Code reviews aren't personal; they protect codebase health. When a peer suggests a more idiomatic or performant approach, I ask clarifying questions to understand their reasoning and incorporate the pattern into future implementations.",
                "star": "Mindset: Code quality over ego -> Action: Understand architectural rationale -> Outcome: Better code and accelerated personal growth."
            },
            {
                "text": "Give an example of a time you showed initiative without being asked.",
                "cat": "Behavioral & STAR",
                "tips": "Highlight spotting an inefficiency, proposing a solution, and executing it proactively.",
                "example": "Situation: During our semester group projects, team members frequently wasted time setting up local virtual environments and installing mismatching library versions. Task: I wanted to streamline developer onboarding. Action: I authored a comprehensive README, created requirements.txt, and created an automated setup script that initializes the virtualenv and seeds sample data in one command. Result: Onboarding time dropped from over an hour to under two minutes.",
                "star": "Observation: Environment setup friction -> Initiative: Automated setup & seed script -> Impact: Onboarding under 2 minutes."
            },
            {
                "text": "What motivates you as a software engineer?",
                "cat": "Introduction & Background",
                "tips": "Connect personal passion for puzzle-solving with the tangible satisfaction of seeing software impact people.",
                "example": "What excites me most is transforming abstract logic into tangible software that solves everyday problems. Seeing students practice interview questions and gain confidence through an application I designed is immensely fulfilling. The constant evolution of technology means there's always a better, faster, and more elegant way to build things.",
                "star": "Core drivers: Problem solving + user impact + continuous intellectual challenge."
            },
            {
                "text": "Are you willing to relocate or work in rotating shifts if required?",
                "cat": "Company & Career Goals",
                "tips": "Be clear, flexible, and honest. Express enthusiasm for starting your career.",
                "example": "Yes, absolutely. As a recent graduate eager to accelerate my career, I am completely open to relocating and flexible with shift schedules. Being present where the team and project need me most is a top priority for me.",
                "star": "Direct, positive, and flexible answer."
            },
            {
                "text": "Tell me about a time you demonstrated leadership.",
                "cat": "Behavioral & STAR",
                "tips": "Leadership isn't just about a title; it's about facilitating consensus, unblocking teammates, and keeping spirits high.",
                "example": "Situation: In our college hackathon, our 4-person team fell behind schedule at the 12-hour mark because two members were stuck on an API authentication bug. Task: We needed to get back on track. Action: I paused our work for a 10-minute standup, helped pair-program through the authentication error, and reassigned sub-tasks to parallelize UI polishing and database seeding. Result: We completed the project with 30 minutes to spare and placed among the top 3 teams.",
                "star": "Situation: Hackathon roadblock -> Action: Standup + pair-programming + parallelizing work -> Result: Top 3 finish."
            },
            {
                "text": "Do you have any questions for us?",
                "cat": "Company & Career Goals",
                "tips": "Ask 2-3 thoughtful questions about the team, tech stack, and onboarding process.",
                "example": "Yes, thank you! 1. How does your engineering team typically onboard entry-level developers during their first 90 days? 2. What are the biggest technical challenges your team is currently tackling with your current architecture? 3. How does the engineering team balance shipping new features with technical debt reduction?",
                "star": "Demonstrates genuine curiosity about team dynamics, technical reality, and onboarding."
            }
        ]

        created_hr = []
        for hr_d in hr_questions_data:
            hr_q = HRQuestion(
                question_text=hr_d['text'],
                category=hr_d['cat'],
                answer_tips=hr_d['tips'],
                example_answer=hr_d['example'],
                star_framework_guide=hr_d['star'],
                created_at=datetime.utcnow() - timedelta(days=20)
            )
            db.session.add(hr_q)
            db.session.flush()
            created_hr.append(hr_q)

        db.session.commit()
        print(f"   Successfully added {len(created_hr)} HR interview questions.")

        # 7. DEMO STUDENT SAMPLE DATA (Authentic, calculated, and verifiable)
        print("   Seeding realistic demo student preparation activity...")

        # A: Student takes Test 1 (Full Stack Mock Test)
        test1 = created_tests[0]
        test1_questions = test1.test_questions.all()
        attempt1 = TestAttempt(
            user_id=student.id,
            test_id=test1.id,
            started_at=datetime.utcnow() - timedelta(days=2, hours=3),
            status='in_progress'
        )
        db.session.add(attempt1)
        db.session.flush()

        # Answers: 12 correct out of 15 (~80%)
        user_answers = {}
        for idx, tq in enumerate(test1_questions):
            q = tq.question
            if idx < 12:
                user_answers[str(q.id)] = q.correct_answer
            else:
                wrong_choice = 'A' if q.correct_answer != 'A' else 'B'
                user_answers[str(q.id)] = wrong_choice

        grade_test_attempt(attempt1.id, user_answers, time_taken_seconds=1150)

        # B: Student solves 2 coding problems
        p1 = created_problems[0]  # Largest Element
        sub1 = CodingSubmission(
            user_id=student.id,
            problem_id=p1.id,
            submitted_code=p1.starter_code,
            language='python',
            result_status='Accepted',
            test_cases_passed=4,
            test_cases_total=4,
            runtime_ms=28.5,
            submitted_at=datetime.utcnow() - timedelta(days=1, hours=4)
        )
        db.session.add(sub1)

        p2 = created_problems[1]  # Reverse String
        sub2 = CodingSubmission(
            user_id=student.id,
            problem_id=p2.id,
            submitted_code=p2.starter_code,
            language='python',
            result_status='Accepted',
            test_cases_passed=4,
            test_cases_total=4,
            runtime_ms=22.1,
            submitted_at=datetime.utcnow() - timedelta(hours=18)
        )
        db.session.add(sub2)

        # C: Student practices 2 HR questions
        hr1 = created_hr[0]
        hr_p1 = HRPractice(
            user_id=student.id,
            hr_question_id=hr1.id,
            personal_answer="I am a final-year CS undergrad passionate about full-stack web development and scalable architectures. I enjoy solving algorithmic challenges and building products that make a real difference for students.",
            is_practiced=True,
            confidence_level="High",
            updated_at=datetime.utcnow() - timedelta(days=1)
        )
        db.session.add(hr_p1)

        hr2 = created_hr[1]
        hr_p2 = HRPractice(
            user_id=student.id,
            hr_question_id=hr2.id,
            personal_answer="My core strengths are deep technical curiosity, proactive problem solving, and writing maintainable, clean code.",
            is_practiced=True,
            confidence_level="Medium",
            updated_at=datetime.utcnow() - timedelta(hours=10)
        )
        db.session.add(hr_p2)

        # D: Student bookmarks 3 questions
        for q_b in created_questions[:3]:
            bm = Bookmark(user_id=student.id, question_id=q_b.id, created_at=datetime.utcnow() - timedelta(days=2))
            db.session.add(bm)

        # E: Student activity logs
        act1 = ActivityLog(
            user_id=student.id,
            activity_type='coding_submission',
            title=f"Solved Coding Challenge: {p1.title}",
            description="Passed 4/4 test cases",
            reference_id=p1.id,
            created_at=datetime.utcnow() - timedelta(days=1, hours=4)
        )
        act2 = ActivityLog(
            user_id=student.id,
            activity_type='coding_submission',
            title=f"Solved Coding Challenge: {p2.title}",
            description="Passed 4/4 test cases",
            reference_id=p2.id,
            created_at=datetime.utcnow() - timedelta(hours=18)
        )
        act3 = ActivityLog(
            user_id=student.id,
            activity_type='hr_practice',
            title=f"Practiced HR Question: {hr1.question_text[:40]}...",
            description="Confidence: High",
            reference_id=hr1.id,
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        db.session.add_all([act1, act2, act3])
        db.session.commit()

        # F: Generate genuine recommendations based on student performance
        print("   Generating smart personalized recommendations...")
        recs = generate_recommendations(student.id)
        print(f"   Generated {len(recs)} rule-based recommendations for student.")

        print("\n========================================================")
        print("[SUCCESS] DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print(f"   - Users: 2 (Admin: admin@smartprep.com, Student: student@smartprep.com)")
        print(f"   - Categories: {Category.query.count()}")
        print(f"   - Questions: {Question.query.count()}")
        print(f"   - Mock Tests: {MockTest.query.count()}")
        print(f"   - Coding Problems: {CodingProblem.query.count()}")
        print(f"   - HR Questions: {HRQuestion.query.count()}")
        print("========================================================\n")

if __name__ == '__main__':
    run_seed()

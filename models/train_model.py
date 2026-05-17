"""
Smart Interview Simulator — ML Model Training Script
=====================================================
Trains and saves three scikit-learn models:
  1. topic_classifier.joblib        — classifies an answer into a topic category
  2. answer_quality_classifier.joblib — rates answer quality (poor/average/good)
  3. difficulty_predictor.joblib    — predicts question difficulty (easy/medium/hard)

Run:
    python models/train_model.py
"""

import os
import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score
import numpy as np

# ─────────────────────────────────────────────────────────────
# MODEL 1 TRAINING DATA — Topic Classifier
# Categories: programming, web_development, database,
#             data_science, software_testing, oop,
#             algorithms, operating_system, general
# ─────────────────────────────────────────────────────────────
TOPIC_DATA = [
    # programming
    ("A variable is a named storage location in memory that holds a value.", "programming"),
    ("We use let, const, and var in JavaScript to declare variables.", "programming"),
    ("A function is a reusable block of code that performs a specific task.", "programming"),
    ("Parameters are the inputs a function accepts when it is called.", "programming"),
    ("A loop repeats a block of code multiple times based on a condition.", "programming"),
    ("The for loop iterates over a range or collection of items.", "programming"),
    ("The while loop continues executing as long as the condition is true.", "programming"),
    ("A conditional statement executes different code based on a boolean condition.", "programming"),
    ("If-else statements allow the program to make decisions at runtime.", "programming"),
    ("Recursion is when a function calls itself to solve a smaller sub-problem.", "programming"),
    ("A recursive function must have a base case to stop infinite calls.", "programming"),
    ("Arrays store multiple elements of the same type in contiguous memory.", "programming"),
    ("In Python, lists are dynamic arrays that can hold mixed data types.", "programming"),
    ("String manipulation includes slicing, concatenation, and formatting.", "programming"),
    ("Type casting converts a value from one data type to another.", "programming"),
    ("Exception handling in Python uses try, except, finally blocks.", "programming"),
    ("A pointer stores the memory address of another variable.", "programming"),
    ("Pass by value copies the value; pass by reference copies the address.", "programming"),
    ("Lambda functions are anonymous single-expression functions in Python.", "programming"),
    ("List comprehensions provide a concise way to create lists in Python.", "programming"),

    # web_development
    ("HTML provides the structure of a web page using tags and elements.", "web_development"),
    ("CSS is used to style and layout HTML elements on the page.", "web_development"),
    ("JavaScript adds interactivity and dynamic behavior to web pages.", "web_development"),
    ("React is a component-based JavaScript library for building UIs.", "web_development"),
    ("A REST API uses HTTP methods like GET, POST, PUT, DELETE.", "web_development"),
    ("API stands for Application Programming Interface.", "web_development"),
    ("MVC stands for Model View Controller and organizes application layers.", "web_development"),
    ("JSON is a lightweight data interchange format used in web APIs.", "web_development"),
    ("Node.js allows JavaScript to run on the server outside the browser.", "web_development"),
    ("Express.js is a minimal web framework built on top of Node.js.", "web_development"),
    ("CORS stands for Cross-Origin Resource Sharing and controls API access.", "web_development"),
    ("HTTP status codes like 200, 404, and 500 describe response outcomes.", "web_development"),
    ("A session stores user state on the server between requests.", "web_development"),
    ("Cookies are small pieces of data stored by the browser.", "web_development"),
    ("WebSockets enable full-duplex communication between client and server.", "web_development"),
    ("The DOM represents the HTML document as a tree of objects.", "web_development"),
    ("Responsive design ensures a website looks good on all screen sizes.", "web_development"),
    ("AJAX allows asynchronous requests to the server without reloading the page.", "web_development"),
    ("Vue.js is a progressive JavaScript framework for building user interfaces.", "web_development"),
    ("Angular is a full-featured TypeScript-based frontend framework by Google.", "web_development"),
    ("FastAPI is a modern Python framework for building APIs quickly.", "web_development"),
    ("Authentication tokens like JWT are used to secure REST API endpoints.", "web_development"),

    # database
    ("SQL is the standard language for querying relational databases.", "database"),
    ("SQL stands for Structured Query Language.", "database"),
    ("DBMS stands for Database Management System.", "database"),
    ("A primary key uniquely identifies each record in a database table.", "database"),
    ("A foreign key creates a relationship between two tables.", "database"),
    ("Normalization reduces data redundancy by organizing tables efficiently.", "database"),
    ("An index speeds up database query performance on large tables.", "database"),
    ("A JOIN clause combines rows from two or more tables based on a condition.", "database"),
    ("INNER JOIN returns records that have matching values in both tables.", "database"),
    ("LEFT JOIN returns all records from the left table and matched right records.", "database"),
    ("MongoDB is a NoSQL database that stores data in BSON documents.", "database"),
    ("ACID stands for Atomicity, Consistency, Isolation, and Durability.", "database"),
    ("A transaction groups database operations that must succeed or fail together.", "database"),
    ("Stored procedures are precompiled SQL statements stored in the database.", "database"),
    ("Schema defines the structure of a database including tables and columns.", "database"),
    ("Triggers automatically execute SQL when a specific event occurs.", "database"),
    ("GROUP BY aggregates rows sharing the same values into summary rows.", "database"),
    ("Database sharding splits a large database across multiple servers.", "database"),
    ("Replication copies data across multiple database servers for redundancy.", "database"),
    ("A view is a virtual table based on the result of a SQL query.", "database"),
    ("The SELECT statement retrieves data from one or more tables.", "database"),
    ("PostgreSQL is an open-source relational database with advanced features.", "database"),

    # data_science
    ("Machine learning allows systems to learn from data and make predictions.", "data_science"),
    ("Supervised learning uses labeled data to train a prediction model.", "data_science"),
    ("Unsupervised learning finds hidden patterns in unlabeled data.", "data_science"),
    ("A neural network is a series of algorithms modeled after the human brain.", "data_science"),
    ("Deep learning uses multi-layer neural networks to learn complex patterns.", "data_science"),
    ("Overfitting occurs when a model learns noise in the training data.", "data_science"),
    ("Underfitting occurs when a model is too simple to capture the data pattern.", "data_science"),
    ("Cross-validation evaluates model performance using multiple train-test splits.", "data_science"),
    ("Precision measures the accuracy of positive predictions in classification.", "data_science"),
    ("Recall measures the proportion of actual positives that were identified.", "data_science"),
    ("The F1 score is the harmonic mean of precision and recall.", "data_science"),
    ("A confusion matrix shows correct and incorrect predictions by class.", "data_science"),
    ("Feature engineering creates new input variables to improve model accuracy.", "data_science"),
    ("PCA reduces the dimensionality of data while preserving variance.", "data_science"),
    ("PCA stands for Principal Component Analysis.", "data_science"),
    ("The bias-variance tradeoff balances model complexity and generalization.", "data_science"),
    ("Random forests use an ensemble of decision trees for robust predictions.", "data_science"),
    ("Gradient boosting builds trees sequentially, each correcting prior errors.", "data_science"),
    ("TensorFlow and PyTorch are popular frameworks for deep learning.", "data_science"),
    ("A train-test split separates data for model training and evaluation.", "data_science"),
    ("Hyperparameter tuning adjusts model settings to optimize performance.", "data_science"),

    # software_testing
    ("Unit testing verifies individual functions or methods work correctly.", "software_testing"),
    ("Integration testing checks that combined modules work together.", "software_testing"),
    ("System testing validates the complete and integrated software product.", "software_testing"),
    ("Acceptance testing checks that the system meets business requirements.", "software_testing"),
    ("Regression testing ensures new changes do not break existing features.", "software_testing"),
    ("Test-driven development writes tests before writing the actual code.", "software_testing"),
    ("TDD stands for Test Driven Development.", "software_testing"),
    ("A test case defines input, execution steps, and expected output.", "software_testing"),
    ("Selenium automates browser interaction for web application testing.", "software_testing"),
    ("A bug is an error in software that causes incorrect or unexpected behavior.", "software_testing"),
    ("The bug life cycle includes new, assigned, fixed, verified, and closed.", "software_testing"),
    ("Performance testing evaluates system behavior under load or stress.", "software_testing"),
    ("Smoke testing verifies the basic critical functions of the application.", "software_testing"),
    ("Boundary value analysis tests at the edges of valid input ranges.", "software_testing"),
    ("Equivalence partitioning divides inputs into classes that behave the same.", "software_testing"),
    ("A test plan documents the scope, approach, and schedule for testing.", "software_testing"),
    ("Continuous integration runs automated tests on every code commit.", "software_testing"),
    ("Security testing finds vulnerabilities and weaknesses in the system.", "software_testing"),
    ("Black box testing evaluates functionality without knowledge of internal code.", "software_testing"),
    ("White box testing examines internal code structure and logic paths.", "software_testing"),
    ("API testing validates request and response behavior of web service endpoints.", "software_testing"),

    # oop
    ("A class is a blueprint for creating objects with shared attributes.", "oop"),
    ("An object is an instance of a class with specific state and behavior.", "oop"),
    ("Encapsulation bundles data and methods inside a class, hiding internals.", "oop"),
    ("Abstraction hides complex implementation and exposes only the interface.", "oop"),
    ("Inheritance allows a subclass to reuse properties and methods of a parent.", "oop"),
    ("Polymorphism allows the same method to behave differently for different types.", "oop"),
    ("Method overriding lets a subclass redefine a parent class method.", "oop"),
    ("Method overloading defines multiple methods with the same name but different params.", "oop"),
    ("A constructor initializes object state when a new instance is created.", "oop"),
    ("An interface defines a contract of methods that implementing classes must follow.", "oop"),
    ("An abstract class cannot be instantiated and must be subclassed.", "oop"),
    ("The static keyword makes a method or attribute belong to the class itself.", "oop"),
    ("The self keyword in Python refers to the current instance of the class.", "oop"),
    ("Design patterns like Singleton ensure only one instance of a class exists.", "oop"),
    ("The Factory pattern creates objects without specifying their exact class.", "oop"),
    ("SOLID principles guide writing maintainable and scalable object-oriented code.", "oop"),
    ("Composition over inheritance prefers building classes from components.", "oop"),
    ("A destructor cleans up resources when an object is no longer needed.", "oop"),
    ("Access modifiers like private, protected, and public control visibility.", "oop"),
    ("Dependency injection passes dependencies into a class from outside.", "oop"),

    # algorithms
    ("Binary search finds an element in a sorted array in O(log n) time.", "algorithms"),
    ("Bubble sort repeatedly swaps adjacent elements until sorted.", "algorithms"),
    ("Merge sort divides the array, sorts halves, and merges them back.", "algorithms"),
    ("Quick sort picks a pivot and partitions elements around it recursively.", "algorithms"),
    ("Big O notation describes the worst-case time complexity of an algorithm.", "algorithms"),
    ("Dynamic programming solves problems by storing results of sub-problems.", "algorithms"),
    ("A greedy algorithm picks the locally optimal choice at each step.", "algorithms"),
    ("A stack follows Last In First Out (LIFO) order.", "algorithms"),
    ("A queue follows First In First Out (FIFO) order.", "algorithms"),
    ("A linked list is a chain of nodes where each node points to the next.", "algorithms"),
    ("A binary tree has at most two children per node.", "algorithms"),
    ("A hash table stores key-value pairs using a hash function for fast access.", "algorithms"),
    ("Graph traversal algorithms include BFS and DFS.", "algorithms"),
    ("Breadth-first search explores neighbors level by level.", "algorithms"),
    ("Depth-first search explores as far as possible down each branch first.", "algorithms"),
    ("Dijkstra's algorithm finds the shortest path in a weighted graph.", "algorithms"),
    ("Space complexity measures the memory used by an algorithm.", "algorithms"),
    ("Time complexity measures how runtime grows with input size.", "algorithms"),
    ("A heap is a tree-based data structure that satisfies the heap property.", "algorithms"),
    ("Two pointers technique efficiently solves array problems in linear time.", "algorithms"),

    # operating_system
    ("An operating system manages hardware resources and software processes.", "operating_system"),
    ("A process is a program in execution with its own memory space.", "operating_system"),
    ("A thread is a lightweight unit of execution within a process.", "operating_system"),
    ("Multithreading allows concurrent execution of multiple threads.", "operating_system"),
    ("Deadlock occurs when processes wait forever for each other's resources.", "operating_system"),
    ("A semaphore is a synchronization primitive to control resource access.", "operating_system"),
    ("A mutex prevents simultaneous access to a shared resource.", "operating_system"),
    ("Virtual memory allows a process to use more memory than physically available.", "operating_system"),
    ("Paging divides memory into fixed-size pages for virtual memory management.", "operating_system"),
    ("The CPU scheduler decides which process runs next on the processor.", "operating_system"),
    ("Round-robin scheduling gives each process a fixed time slice.", "operating_system"),
    ("Context switching saves and restores process state when switching CPU.", "operating_system"),
    ("A race condition occurs when output depends on unpredictable thread timing.", "operating_system"),
    ("Interprocess communication allows processes to exchange data.", "operating_system"),
    ("File systems organize and store data on disk storage devices.", "operating_system"),
    ("A system call is the interface between a user program and the OS kernel.", "operating_system"),
    ("The kernel is the core of the OS that manages hardware and processes.", "operating_system"),
    ("Swapping moves processes between main memory and disk storage.", "operating_system"),
    ("Cache memory stores frequently accessed data for faster CPU access.", "operating_system"),
    ("Memory fragmentation occurs when free memory is split into small non-contiguous blocks.", "operating_system"),

    # general (low-effort / off-topic)
    ("I don't know the answer to this question.", "general"),
    ("I'm not sure how to approach this.", "general"),
    ("I have never worked with that technology before.", "general"),
    ("I don't remember the exact definition.", "general"),
    ("It's a good practice in software development.", "general"),
    ("Yes, I agree with that statement.", "general"),
    ("That sounds correct to me.", "general"),
    ("I haven't studied this topic in detail.", "general"),
    ("I think it involves something related to computers.", "general"),
    ("I cannot recall the specifics right now.", "general"),
]

# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
# MODEL 2 TRAINING DATA \u2014 Answer Quality Classifier
# Labels: poor, average, good
# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
QUALITY_DATA = [
    # \u2500\u2500 GOOD answers (40+ words, multiple key concepts, examples, structured) \u2500\u2500
    ("Object-oriented programming organizes code into classes and objects. It uses inheritance to share behavior, encapsulation to hide implementation details, and polymorphism to allow different types to be treated uniformly.", "good"),
    ("A REST API uses HTTP methods: GET to retrieve data, POST to create, PUT to update, and DELETE to remove resources. Each endpoint represents a resource and responses are typically in JSON format.", "good"),
    ("SQL JOIN combines rows from two tables based on a related column. INNER JOIN returns only matching rows, LEFT JOIN returns all rows from the left table plus matches from the right.", "good"),
    ("Machine learning is a subset of AI where algorithms learn patterns from data. Supervised learning uses labeled examples while unsupervised learning finds hidden patterns. Neural networks are used for complex tasks.", "good"),
    ("Unit testing verifies individual components of code work as expected. It uses assertions to check output, isolates dependencies with mocks, and is automated using frameworks like pytest or JUnit.", "good"),
    ("Recursion is when a function calls itself with a smaller input. It needs a base case to stop infinite calls. For example, factorial of n equals n times factorial of n minus one, stopping at zero.", "good"),
    ("A hash table stores key-value pairs using a hash function to compute the array index. Collisions are handled with chaining or open addressing. Average lookup time is O of one which is very efficient.", "good"),
    ("Virtual memory allows a process to use more memory than physically available by using disk space as an extension of RAM. The OS uses paging to map virtual addresses to physical memory locations.", "good"),
    ("Binary search works on a sorted array by dividing the search space in half each step. If the target is less than the middle element it searches the left half, otherwise the right. Time complexity is O log n.", "good"),
    ("Encapsulation is an OOP principle where an object's data is hidden from outside access. We use private attributes and public getter and setter methods to control access to the internal state.", "good"),
    ("The CAP theorem states that a distributed system can guarantee at most two of Consistency, Availability, and Partition Tolerance. Systems must choose between CP or AP based on their specific requirements.", "good"),
    ("ACID properties ensure reliable database transactions. Atomicity means all or nothing, Consistency ensures valid state transitions, Isolation keeps transactions separate, and Durability persists committed changes.", "good"),
    ("Deep learning uses multi-layer neural networks to learn hierarchical features from data. Convolutional networks handle images, recurrent networks handle sequences, and transformers handle text tasks.", "good"),
    ("The MVC pattern separates an application into Model for data, View for the user interface, and Controller for logic. This separation of concerns makes code easier to maintain and independently test.", "good"),
    ("Multithreading allows a process to run multiple threads concurrently and improves performance. Threads share memory so synchronization with mutexes or semaphores is needed to prevent race conditions.", "good"),
    ("Database normalization removes redundancy by organizing tables. First normal form removes repeating groups, second removes partial dependencies, and third removes transitive dependencies.", "good"),
    ("A deadlock occurs when two or more processes wait indefinitely for resources held by each other forming a cycle. Prevention techniques include resource ordering, timeouts, and deadlock detection algorithms.", "good"),
    ("The difference between a process and a thread is that a process has its own memory space while threads within the same process share memory. Threads are lighter weight and have faster context switching.", "good"),
    ("Overfitting is when a model memorizes training data including noise and fails to generalize to new data. It can be prevented with cross-validation, regularization, dropout layers, and early stopping.", "good"),
    ("Test-driven development is a methodology where tests are written before the production code. The TDD cycle is red meaning write a failing test, green meaning make it pass, then refactor the code.", "good"),
    ("SQL injection is an attack where malicious SQL code is injected into a query. It is prevented by using parameterized queries, prepared statements, and thorough input validation and sanitization.", "good"),
    ("Inheritance allows a child class to reuse properties and methods from a parent class promoting code reuse. For example a Dog class can inherit from an Animal class and add dog-specific behavior.", "good"),
    ("A linked list stores data in nodes where each node contains data and a pointer to the next node. Unlike arrays, it allows efficient insertion and deletion but has O of n lookup time.", "good"),
    ("Big O notation describes worst-case time complexity as input size grows. O of one is constant, O log n is logarithmic, O of n is linear, O n log n is typical for good sorting, and O n squared is quadratic.", "good"),

    # \u2500\u2500 AVERAGE answers (15-40 words, partially correct, lacks depth or examples) \u2500\u2500
    ("OOP is a programming style that uses objects and classes to organize code. It has inheritance and encapsulation which are useful for code reuse.", "average"),
    ("A REST API is an interface for communicating between systems using HTTP. It uses JSON to send and receive data from the server.", "average"),
    ("A JOIN in SQL is used to combine data from multiple tables. There are inner joins and left joins which are used differently.", "average"),
    ("Machine learning is when a computer learns from data to make predictions. There are different types like supervised and unsupervised learning.", "average"),
    ("Unit testing means testing each part of your code separately. It helps find bugs early in development.", "average"),
    ("Recursion is when a function calls itself. You need a base case to stop it from running forever.", "average"),
    ("A hash table is a data structure that stores key-value pairs and uses a hash function to find data quickly.", "average"),
    ("Virtual memory is when the operating system uses disk space as extra memory when RAM is full.", "average"),
    ("Binary search is an efficient search algorithm that works on sorted arrays by dividing them in half each step.", "average"),
    ("Encapsulation means hiding the data inside a class using private variables and exposing it through public methods.", "average"),
    ("ACID properties are important for database transactions to ensure data integrity and reliability.", "average"),
    ("Deep learning is a type of machine learning that uses neural networks with many hidden layers.", "average"),
    ("Application Programming Interface is the full form of API.", "average"),
    ("MVC stands for Model View Controller. It is a design pattern used to organize code in web applications.", "average"),
    ("Model View Controller ", "average"),
    ("Structured Query Language ", "average"),
    ("Database Management System ", "average"),
    ("HyperText Markup Language ", "average"),
    ("Cascading Style Sheets ", "average"),
    ("Principal Component Analysis ", "average"),
    ("Test Driven Development .", "average"),
    ("Atomicity Consistency Isolation and Durability are the ACID properties.", "average"),
    ("Consistency Availability and Partition Tolerance are the CAP theorem terms.", "average"),
    ("Threads allow a program to do multiple things at the same time within the same process.", "average"),
    ("Normalization is the process of organizing a database to reduce data redundancy and improve structure.", "average"),
    ("Inheritance allows a subclass to acquire properties and methods of a parent class to reuse code.", "average"),
    ("A linked list stores data in nodes where each node points to the next node. It differs from arrays.", "average"),
    ("Overfitting is when a model performs well on training data but poorly on unseen test data.", "average"),
    ("Deadlock happens when two processes are waiting for resources held by each other and cannot proceed.", "average"),
    ("SQL injection is an attack where harmful SQL code is injected into a database query input.", "average"),

    # \u2500\u2500 POOR answers (vague, too short, or factually WRONG) \u2500\u2500
    # Vague / no-knowledge answers
    ("I don't know.", "poor"),
    ("I am not sure about this topic.", "poor"),
    ("I have not studied this in detail.", "poor"),
    ("Not sure about this.", "poor"),
    ("I do not remember the definition.", "poor"),
    ("I have no idea how this works.", "poor"),
    ("I think it involves computers somehow.", "poor"),
    ("It is a programming concept.", "poor"),
    ("It is used in software development.", "poor"),
    ("Maybe it is related to the internet.", "poor"),
    ("Computers use this for something.", "poor"),
    ("It is some kind of framework or tool.", "poor"),
    # Factually WRONG but technical-sounding answers
    ("OOP is a technique to optimize SQL queries by joining database tables for faster results.", "poor"),
    ("Machine learning is when the CPU processes HTML and CSS files faster using GPU acceleration cores.", "poor"),
    ("A variable is a type of JOIN operation in SQL used to merge two relational database tables.", "poor"),
    ("Recursion is a JavaScript web framework used to build REST APIs similar to Express.js and Flask.", "poor"),
    ("Inheritance is when you normalize database tables to remove redundancy following 1NF and 2NF rules.", "poor"),
    ("Encapsulation is the process of encrypting network data using SSL and TLS certificates for security.", "poor"),
    ("Binary search is a sorting algorithm that uses a pivot element to partition arrays like quicksort.", "poor"),
    ("A hash table is a type of neural network layer used in deep learning models for image classification.", "poor"),
    ("Polymorphism is a database property that ensures atomicity and consistency in SQL transactions.", "poor"),
    ("Unit testing is a Docker container deployment strategy used to isolate and scale microservices.", "poor"),
    ("Deadlock is when a SQL query runs too long and the database index fails to respond in time.", "poor"),
    ("Normalization in machine learning means converting input images to grayscale format before CNN training.", "poor"),
]


# ─────────────────────────────────────────────────────────────
# MODEL 3 TRAINING DATA — Question Difficulty Predictor
# Derived from questions.json categories + synthetic additions
# Labels: easy, medium, hard
# ─────────────────────────────────────────────────────────────
DIFFICULTY_DATA = [
    # easy
    ("What is a variable in programming?", "easy"),
    ("What is HTML?", "easy"),
    ("What is CSS?", "easy"),
    ("What is a function?", "easy"),
    ("What is a loop in programming?", "easy"),
    ("What is an array?", "easy"),
    ("What is a database?", "easy"),
    ("What is Object-Oriented Programming?", "easy"),
    ("What is an API?", "easy"),
    ("What is version control?", "easy"),
    ("What is software testing?", "easy"),
    ("What is a bug?", "easy"),
    ("What is a test case?", "easy"),
    ("What is data analysis?", "easy"),
    ("What is a dataset?", "easy"),
    ("What is data cleaning?", "easy"),
    ("What is a programming language?", "easy"),
    ("What is an algorithm?", "easy"),
    ("What is a data structure?", "easy"),
    ("What is a conditional statement?", "easy"),
    ("What is smoke testing?", "easy"),
    ("What is a test plan?", "easy"),
    ("What is sorting in data analysis?", "easy"),
    ("What is filtering data?", "easy"),
    ("What is a chart or graph?", "easy"),
    ("What is a spreadsheet?", "easy"),
    ("What is a pointer?", "easy"),
    ("Explain what a loop is.", "easy"),
    ("What is the difference between data and information?", "easy"),

    # medium
    ("Explain the difference between REST and SOAP APIs.", "medium"),
    ("What is SQL injection and how can you prevent it?", "medium"),
    ("Explain the concept of recursion with an example.", "medium"),
    ("What is the difference between GET and POST methods?", "medium"),
    ("Explain ACID properties in databases.", "medium"),
    ("What is the difference between inner join and left join?", "medium"),
    ("Explain the concept of authentication vs authorization.", "medium"),
    ("What is the purpose of indexing in databases?", "medium"),
    ("Explain the MVC architecture pattern.", "medium"),
    ("What is the difference between stack and heap memory?", "medium"),
    ("Explain the different levels of testing.", "medium"),
    ("What is regression testing and when is it performed?", "medium"),
    ("Explain the concept of test-driven development.", "medium"),
    ("What is boundary value analysis?", "medium"),
    ("What is equivalence partitioning?", "medium"),
    ("Explain the difference between correlation and causation.", "medium"),
    ("What are the measures of central tendency?", "medium"),
    ("What is a pivot table used for?", "medium"),
    ("Explain the concept of data visualization and its importance.", "medium"),
    ("Explain the difference between array and linked list.", "medium"),
    ("What is time complexity and space complexity?", "medium"),
    ("What is DBMS?", "medium"),
    ("Explain the difference between SQL and NoSQL databases.", "medium"),
    ("What is the difference between functional and non-functional testing?", "medium"),
    ("Explain the difference between verification and validation.", "medium"),
    ("What is outlier detection?", "medium"),
    ("Explain the concept of sorting algorithms.", "medium"),
    ("What is a pointer in C and how does it work?", "medium"),

    # hard
    ("Explain microservices architecture and its advantages over monolithic architecture.", "hard"),
    ("What is the CAP theorem and how does it apply to distributed systems?", "hard"),
    ("Explain the concept of dependency injection and its benefits.", "hard"),
    ("What are design patterns? Explain Singleton and Factory patterns.", "hard"),
    ("Explain the working of a hash table and how collisions are handled.", "hard"),
    ("Explain the concept of race conditions and how to prevent them.", "hard"),
    ("What is eventual consistency in distributed systems?", "hard"),
    ("Explain the concept of containerization and its benefits.", "hard"),
    ("What is the difference between synchronous and asynchronous programming?", "hard"),
    ("Explain the concept of message queues and their use cases.", "hard"),
    ("Explain the concept of hypothesis testing and p-value.", "hard"),
    ("Explain the bias-variance tradeoff in machine learning.", "hard"),
    ("What is time series analysis and when is it used?", "hard"),
    ("Explain the concept of feature engineering in machine learning.", "hard"),
    ("What is the difference between regression and classification?", "hard"),
    ("Explain the concept of cross-validation in machine learning.", "hard"),
    ("What is dimensionality reduction? Explain PCA.", "hard"),
    ("Explain the different types of test automation frameworks.", "hard"),
    ("Explain the concept of continuous integration and continuous deployment.", "hard"),
    ("What is performance testing and what are its types?", "hard"),
    ("Explain the bug life cycle in software testing.", "hard"),
    ("What is security testing and what are its types?", "hard"),
    ("What is the difference between black box and white box testing?", "hard"),
    ("Explain the working of binary search algorithm with time complexity.", "hard"),
    ("Explain the concept of virtual memory in operating systems.", "hard"),
    ("What is deadlock in operating systems and how can it be prevented?", "hard"),
    ("Explain the concept of normalization in databases with 1NF, 2NF, 3NF.", "hard"),
    ("Explain the difference between process and thread in operating systems.", "hard"),
    ("What is the difference between supervised and unsupervised learning?", "hard"),
]


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))


def _build_pipeline() -> object:
    return make_pipeline(
        TfidfVectorizer(stop_words="english", max_features=3000, ngram_range=(1, 2)),
        LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    )


def _train_and_save(name: str, data: list, filename: str) -> None:
    print(f"\n{'='*55}")
    print(f"  Training: {name}")
    print(f"{'='*55}")

    X, y = zip(*data)
    pipeline = _build_pipeline()

    # Cross-validation (3-fold) for an honest accuracy estimate
    cv_scores = cross_val_score(pipeline, X, y, cv=3, scoring="accuracy")
    print(f"  Cross-Val Accuracy : {cv_scores.mean() * 100:.1f}% "
          f"(±{cv_scores.std() * 100:.1f}%)")

    # Train on full data before saving
    pipeline.fit(X, y)
    train_acc = pipeline.score(X, y)
    print(f"  Train Accuracy     : {train_acc * 100:.1f}%")
    print(f"  Classes            : {sorted(set(y))}")
    print(f"  Samples            : {len(X)}")

    out_path = os.path.join(MODEL_DIR, filename)
    joblib.dump(pipeline, out_path)
    print(f"  Saved → {out_path}")


# ─────────────────────────────────────────────────────────────
# Optionally augment difficulty data from questions.json
# ─────────────────────────────────────────────────────────────
def _load_questions_json() -> list:
    """Load (text, difficulty) pairs from dataset/questions.json."""
    pairs = []
    dataset_path = os.path.join(
        os.path.dirname(MODEL_DIR), "dataset", "questions.json"
    )
    if not os.path.exists(dataset_path):
        return pairs
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for role_data in data.values():
        for difficulty in ("easy", "medium", "hard"):
            for q in role_data.get(difficulty, []):
                text = q.get("text", "").strip()
                if text:
                    pairs.append((text, difficulty))
    return pairs


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def train_all_models():
    print("\n🚀  Smart Interview Simulator — ML Model Trainer")
    print("=" * 55)

    # Model 1: Topic Classifier
    _train_and_save(
        "Topic Classifier",
        TOPIC_DATA,
        "topic_classifier.joblib",
    )

    # Model 2: Answer Quality Classifier
    _train_and_save(
        "Answer Quality Classifier",
        QUALITY_DATA,
        "answer_quality_classifier.joblib",
    )

    # Model 3: Difficulty Predictor (augmented from questions.json)
    json_pairs = _load_questions_json()
    combined_difficulty = DIFFICULTY_DATA + json_pairs
    # De-duplicate
    seen = set()
    deduped = []
    for text, label in combined_difficulty:
        if text not in seen:
            seen.add(text)
            deduped.append((text, label))

    _train_and_save(
        "Question Difficulty Predictor",
        deduped,
        "difficulty_predictor.joblib",
    )

    print("\n✅  All models trained and saved successfully.")
    print(f"    Output directory: {MODEL_DIR}\n")


if __name__ == "__main__":
    train_all_models()

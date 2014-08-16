Bouwer Tutorial
================

This page gives a introduction how to use bouwer for simple C/C++ development. Make sure you have bouwer installed on
your system:

.. code-block:: bash

  $ git clone https://github.com/nieklinnenbank/bouwer

If you want to invoke bouwer by simply calling ``bouw`` on the commandline, make an alias in ``bash``:

.. code-block:: bash

  $ alias bouw=/path/to/bouwer.git/bouw

To view all available

Hello World
-----------

First we make a hello world C program. Open your favorite text editor and create the file ``hello.c``:

.. literalinclude:: hello.c
   :language: c
   :linenos:

To build a C program using Bouwer, you must create a ``Bouwfile`` which describes how to build it. Create
a file called ``Bouwfile`` in the same directory as the ``hello.c`` file:

.. code-block:: python
   :linenos:

   def build(conf):
       Program('hello.c')

Now you need to run Bouwer to let it read the ``Bouwfile`` and compile the Hello world program. Type
the following command on your terminal:

.. code-block:: bash

   $ bouw
       CC  hello.o
     LINK  hello

The hello world program is now compiled! Run it to test:

.. code-block:: bash

   $ ./hello
   Hello world!

If you run bouwer again, you will see it will not re-compile the Hello world program, until you actually change the source code:

.. code-block:: bash

   $ bouw
   $ touch hello.c
   $ bouw
       CC  hello.o
     LINK  hello

Adding configuration
--------------------
Make it configurable.

Changing configuration
----------------------
Change some variables. Change compiler. etc.

Adding build targets
--------------------
Show that you can have multiple build targets.. easy

Customizing build output
---------------------
Show progress bar. Pretty output. Full output. etc.

Prebuild Compiler checks
------------------------
Autoconf a like stuff

Linking with a library
----------------------
Add a library. Then let it link with hello world.

Separating into Subdirectories
------------------------------
How to change the project into separate directory

Installing files
----------------

Creating a source archive (.tar.gz)
-----------------------------------

Adding configuration trees (debug/release)
------------------------------------------

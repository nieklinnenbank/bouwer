_GCC 		 = $(CROSS)gcc
#_CFLAGS 	 = -g3 -O0 -Wall -MD $(CFLAGS)
_CFLAGS      = -Wall $(CFLAGS)
_CPPFLAGS 	 = $(CPPFLAGS) -I.
_LDFLAGS	 = $(LDFLAGS)
_CXXFLAGS        = $(CXXFLAGS)

_C_SOURCES	 = $(wildcard *.c)
_CPP_SOURCES	 = $(wildcard *.cpp)
_S_SOURCES	 = $(wildcard *.S)
_DEPS		 = $(wildcard *.d)
_C_OBJECTS	 = $(patsubst %.c,%.o,$(_C_SOURCES))
_CPP_OBJECTS     = $(patsubst %.cpp,%.o,$(_CPP_SOURCES))
_S_OBJECTS	 = $(patsubst %.S,%.o,$(_S_SOURCES))

_GCC_TARGET	 = hello
_OBJECTS	+= $(_C_OBJECTS) $(_S_OBJECTS) $(_CPP_OBJECTS)

$(_GCC_TARGET) : $(_C_OBJECTS) $(_CPP_OBJECTS) $(_S_OBJECTS)
	$(_GCC) $(_CFLAGS) $(_CPPFLAGS) $(_LDFLAGS) -o $@ $(_OBJECTS)

$(_C_OBJECTS) : %.o : %.c
	$(_GCC) $(_CFLAGS) $(_CPPFLAGS) -o $@ -c $<
#	$(_GCC) $(_CFLAGS) $(_CPPFLAGS) -o $@ -MQ $@ -c $<


$(_CPP_OBJECTS) : %.o : %.cpp
	$(_GCC) $(_CFLAGS) $(_CPPFLAGS) $(CXXFLAGS) -o $@ -MQ $@ -c $<

$(_S_OBJECTS) : %.o : %.S
	$(_GCC) $(_CFLAGS) $(_CPPFLAGS) -o $@ -MQ $@ -c $<

-include $(_DEPS)


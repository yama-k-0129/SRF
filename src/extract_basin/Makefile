FC = gfortran
FFLAGS = -fopenmp -ffree-line-length-none
SRCS = m_common.f90 find_basin.f90 main.f90
OBJS = $(SRCS:.f90=.o)
TARGET = extract_basin.exe

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(FC) $(FFLAGS) -o $@ $^ -static-libgfortran

%.o: %.f90
	$(FC) $(FFLAGS) -c $<

clean:
	rm -f $(OBJS) $(TARGET)
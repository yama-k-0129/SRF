!**********************************************************************
!
!   Copyright (c) 2024 yama-k-0129
!   Copyright (c) 2021 Kazutake Asahi
!   MIT License : https://opensource.org/licenses/mit-license.php 
!	Usage $extract_basin [dir_file_name] [ip0] [jp0]
!	dir_file_name : file name for dir data set
!	ip0 : "i index" for the downstream edge point
!	jp0 : "j index" for the downstream edge point
!
!**********************************************************************
	program extract_basin
	use m_common
	implicit none
	integer :: i, j
	character(len=125)::buf, buf0
	integer :: isw
	
	integer :: ip0, jp0
	integer :: iarg
	character(len=1024) :: fname0	!for input
	character(len=1024) :: fname1	!for output
	character(len=1024) :: fname2	!for input
	character(len=1024) :: fname3	!for input
	integer :: ni1, nj1
	integer :: imin, imax, jmin, jmax
	real*8  :: xl1, yl1

!==================================================
	!default value set
	ip0 = 2780; jp0 = 1304
	fname0 = "dir.txt"

!--------------------------------------------------
!get args
!--------------------------------------------------
	iarg = iargc()
	if(iarg==5)then					!for gfortran
		call getarg(1, fname0)		!for gfortran
		call getarg(2, buf)			!for gfortran
		read (buf,*) ip0
		call getarg(3, buf)			!for gfortran
		read (buf,*) jp0
		call getarg(4, fname2)  ! First additional file
        call getarg(5, fname3)  ! Second additional file
	else
		write(*,*) "Usage of extract_basin is as follow"
		write(*,*) "$extract_basin [dir_file_name] [ip0] [jp0] [dem_file_name] [landuse_file_name]"
		stop
	endif

!--------------------------------------------------
! NODATA_value�̎w��L���`�F�b�N
!--------------------------------------------------
	open(1, file=trim(fname0))
	read(1,*) buf, buf
	read(1,*) buf, buf
	read(1,*) buf, buf
	read(1,*) buf, buf
	read(1,*) buf, buf
	read(1,*) buf0, buf
	close(1)
	
	if(buf0(1:12) == "NODATA_value")then
		!NODATA_value�̎w�肠��
		isw = 1
	else
		!NODATA_value�̎w��Ȃ�
		isw = -1
	end if
	
!--------------------------------------------------
! �t�@�C���Ǎ��J�n
!--------------------------------------------------
	write(*,*) ""
	write(*,*) "1.start reading DIR data."
	write(*,*) ""
	open(1, file=trim(fname0))
	!open(1, file="data.asc")
	read(1,*) buf, nj
	read(1,*) buf, ni
	read(1,*) buf, xl
	read(1,*) buf, yl
	read(1,*) buf, csize
	if(isw == 1) read(1,*) buf, buf		!NODATA_value�̎w�肠��̂�
	
	allocate(idir(1:ni, 1:nj))
	!write(*,*) ni, nj

	do i=1, ni
		read(1,*) (idir(i,j), j=1, nj)
		!write(*,*) i
 	end do
	close(1)

	call reading_data(fname2, dem_data, isw)
	call reading_data_int(fname3, landuse_data, isw)

	write(*,*) ""
	write(*,*) "... end."
	write(*,*) ""
	
	
	! fname1 = trim(fname0)//"_basin.txt"
!--------------------------------------------------
!DIR�f�[�^�𗘗p�������撊�o
!--------------------------------------------------
	write(*,*) ""
	write(*,*) "2.start extracting BASIN from DIR data."
	write(*,*) ""
	allocate(ibasin(1:ni, 1:nj))
	allocate(distance(1:ni, 1:nj)) ! add yama
	ibasin = -9999
	distance = -9999.0d0 ! add yama
	!write(*,*) ip0, jp0
	
	if( (idir(ip0,jp0) == 1)       &
		.or. (idir(ip0,jp0) == 2)	 &
		.or. (idir(ip0,jp0) == 4)  &
		.or. (idir(ip0,jp0) == 8)  &
		.or. (idir(ip0,jp0) == 16) &
		.or. (idir(ip0,jp0) == 32) &
		.or. (idir(ip0,jp0) == 64) &
		.or. (idir(ip0,jp0) == 128) &
		.or. (idir(ip0,jp0) == 0) &
		.or. (idir(ip0,jp0) == 255) &
		.or. (idir(ip0,jp0) == -1) &
	)then
		!write(*,*) ip0, jp0
		distance(ip0,jp0) = 0.0d0 ! add yama
		ibasin(ip0,jp0) = 1
		call find_basin(ip0, jp0, 0.0d0)
		
	else
		write(*,*) "That point does not have any data."
		stop
	end if
	write(*,*) ""
	write(*,*) "... end."
	write(*,*) ""
	
!--------------------------------------------------
!�f�[�^���`�@���@�K�v�ӏ��̂ݒ��o
!--------------------------------------------------
	write(*,*) ""
	write(*,*) "3.start fixing DATA shape."
	write(*,*) ""
	imin = ni; imax = 1
	jmin = nj; jmax = 1
	do i=1,ni
		do j=1, nj
			if(ibasin(i,j) == 1 )then
				if(i < imin) imin = i
				if(i > imax) imax = i
				if(j < jmin) jmin = j
				if(j > jmax) jmax = j
			end if
		end do
	end do

	ni1 = imax - imin + 1
	nj1 = jmax - jmin + 1
	xl1 = xl + csize*(jmin-1)
	yl1 = yl + csize*(ni - imax)
	write(*,*) ""
	write(*,*) "... end."
	write(*,*) ""
	
!--------------------------------------------------
!���ʏo��
!--------------------------------------------------
	write(*,*) ""
	write(*,*) "4.start outputting DATA."
	write(*,*) ""
	open(1, file="log/dir.txt_basin.txt")
	write(1,"(a5, i10)") "ncols", nj1
	write(1,"(a5, i10)") "nrows", ni1
	write(1,"(a9, f20.10)") "xllcorner", xl1
	write(1,"(a9, f20.10)") "yllcorner", yl1
	write(1,"(a8, f20.10)") "cellsize", csize
	write(1,"(a12, i10)") "NODATA_value", -9999
	do i=imin, imax
		write(1,'(10000(i6))') (ibasin(i,j), j=jmin, jmax)
	end do
	close(1)

	! add yama
	open(2, file="log/dir.txt_distance.txt")
    write(2,"(a5, i10)") "ncols", nj1
    write(2,"(a5, i10)") "nrows", ni1
    write(2,"(a9, f20.10)") "xllcorner", xl1
    write(2,"(a9, f20.10)") "yllcorner", yl1
    write(2,"(a8, f20.10)") "cellsize", csize
    write(2,"(a12, f10.1)") "NODATA_value", -9999.0
    do i=imin, imax
        write(2,'(10000(f12.2))') (distance(i,j), j=jmin, jmax)
    end do
    close(2)

	call write_extracted_data("log/dem.txt_extracted.txt", dem_data, imin, imax, jmin, jmax, xl1, yl1)
	call write_extracted_data_int("log/landuse.txt_extracted.txt", landuse_data, imin, imax, jmin, jmax, xl1, yl1)
	
!--------------------------------------------------
!Debug�@�o��	
!--------------------------------------------------
	!open(2, file="dir_chk.txt")
	!write(2,"(a5, i10)") "ncols", nj
	!write(2,"(a5, i10)") "nrows", ni
	!write(2,"(a9, f20.10)") "xllcorner", xl
	!write(2,"(a9, f20.10)") "yllcorner", yl
	!write(2,"(a8, f20.10)") "cellsize", csize
	!write(2,"(a12, i10)") "NODATA_value", -9999
	!do i=1, ni
	!	!write(2,'(10000(i6))') (idir(i,j), j=1, nj)
	!end do
	!close(2)
	
	write(*,*) ""
	write(*,*) "... end."
	write(*,*) ""
	write(*,*) "normal ends."
	
	end program


	
	
	
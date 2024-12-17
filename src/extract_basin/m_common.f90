!**********************************************************************
!
!   Copyright (c) 2021 Kazutake Asahi
!   MIT License : https://opensource.org/licenses/mit-license.php 
!	���ʕϐ�
!
!**********************************************************************
module m_common
	implicit none
	integer :: ni, nj
	real*8  :: xl, yl
	real*8  :: csize
	integer, dimension(:,:), allocatable :: idir
	integer, dimension(:,:), allocatable :: ibasin
	real*8, allocatable :: distance(:,:)  ! add yama
    real*8, allocatable :: dem_data(:,:)	! add yama
    integer, allocatable :: landuse_data(:,:)	! add yama

	contains
	! add yama
    ! Function to convert lat/lon distance to planar distance (meters)
    ! Copyright (c) 2024 yama-k-0129
    function calc_planar_distance(lat1, lon1, lat2, lon2) result(dist)
        implicit none
        real*8, intent(in) :: lat1, lon1, lat2, lon2
        real*8 :: dist
        real*8, parameter :: R = 6371000.0d0  ! Earth radius in meters
        real*8, parameter :: PI = 3.14159265358979323846d0
        real*8 :: dlat, dlon, a, c
        
        ! Convert to radians
        dlat = (lat2 - lat1) * PI / 180.0d0
        dlon = (lon2 - lon1) * PI / 180.0d0
        
        ! Haversine formula
        a = sin(dlat/2.0d0)**2 + cos(lat1 * PI/180.0d0) * cos(lat2 * PI/180.0d0) * sin(dlon/2.0d0)**2
        c = 2.0d0 * atan2(sqrt(a), sqrt(1.0d0-a))
        dist = R * c
    end function

    ! Copyright (c) 2024 yama-k-0129
	subroutine reading_data(filename, data_array, isw)
        implicit none
        character(len=*), intent(in) :: filename
        real*8, allocatable, intent(out) :: data_array(:,:)
        integer, intent(in) :: isw
        
        character(len=125) :: buf, buf0
        integer :: i, j
        
        ! Read header
        open(10, file=trim(filename))
        read(10,*) buf, buf  ! ncols
        read(10,*) buf, buf  ! nrows
        read(10,*) buf, buf  ! xllcorner
        read(10,*) buf, buf  ! yllcorner
        read(10,*) buf, buf  ! cellsize
        if(isw == 1) read(10,*) buf, buf  ! NODATA_value
        
        ! Allocate and read data
        allocate(data_array(1:ni, 1:nj))
        do i=1, ni
            read(10,*) (data_array(i,j), j=1, nj)
        end do
        close(10)
    end subroutine

    ! Copyright (c) 2024 yama-k-0129
	subroutine reading_data_int(filename, data_array, isw)
        implicit none
        character(len=*), intent(in) :: filename
        integer, allocatable, intent(out) :: data_array(:,:)
        integer, intent(in) :: isw
        
        character(len=125) :: buf, buf0
        integer :: i, j
        
        ! Read header
        open(10, file=trim(filename))
        read(10,*) buf, buf  ! ncols
        read(10,*) buf, buf  ! nrows
        read(10,*) buf, buf  ! xllcorner
        read(10,*) buf, buf  ! yllcorner
        read(10,*) buf, buf  ! cellsize
        if(isw == 1) read(10,*) buf, buf  ! NODATA_value
        
        ! Allocate and read data
        allocate(data_array(1:ni, 1:nj))
        do i=1, ni
            read(10,*) (data_array(i,j), j=1, nj)
        end do
        close(10)
    end subroutine

    ! Copyright (c) 2024 yama-k-0129
	subroutine write_extracted_data(filename, data_array, imin, imax, jmin, jmax, xl1, yl1)
        implicit none
        character(len=*), intent(in) :: filename
        real*8, intent(in) :: data_array(:,:)
        integer, intent(in) :: imin, imax, jmin, jmax
        real*8, intent(in) :: xl1, yl1
        integer :: i, j, ni1, nj1
		real*8, allocatable :: masked_data(:,:)
        
        ni1 = imax - imin + 1
        nj1 = jmax - jmin + 1

		allocate(masked_data(imin:imax, jmin:jmax))
        masked_data = -9999.0d0

		! 抽出部分のみのデータをコピー
		do i = imin, imax
            do j = jmin, jmax
                if (ibasin(i,j) == 1) then
                    masked_data(i,j) = data_array(i,j)
                endif
            end do
        end do
        
        open(11, file=trim(filename))
        write(11,"(a5, i10)") "ncols", nj1
        write(11,"(a5, i10)") "nrows", ni1
        write(11,"(a9, f20.10)") "xllcorner", xl1
        write(11,"(a9, f20.10)") "yllcorner", yl1
        write(11,"(a8, f20.10)") "cellsize", csize
        write(11,"(a12, f10.1)") "NODATA_value", -9999.0
        do i=imin, imax
            write(11,'(10000(f12.2))')  (masked_data(i,j), j=jmin, jmax)
        end do
        close(11)

		deallocate(masked_data)
    end subroutine

    ! Copyright (c) 2024 yama-k-0129
	subroutine write_extracted_data_int(filename, data_array, imin, imax, jmin, jmax, xl1, yl1)
        implicit none
        character(len=*), intent(in) :: filename
        integer, intent(in) :: data_array(:,:)
        integer, intent(in) :: imin, imax, jmin, jmax
        real*8, intent(in) :: xl1, yl1
        integer :: i, j, ni1, nj1
		integer, allocatable :: masked_data(:,:)
        
        ni1 = imax - imin + 1
        nj1 = jmax - jmin + 1

		allocate(masked_data(imin:imax, jmin:jmax))
        masked_data = -9999

		! 抽出部分のみデータをコピー
        do i = imin, imax
            do j = jmin, jmax
                if (ibasin(i,j) == 1) then
                    masked_data(i,j) = data_array(i,j)
                endif
            end do
        end do
        
        open(11, file=trim(filename))
        write(11,"(a5, i10)") "ncols", nj1
        write(11,"(a5, i10)") "nrows", ni1
        write(11,"(a9, f20.10)") "xllcorner", xl1
        write(11,"(a9, f20.10)") "yllcorner", yl1
        write(11,"(a8, f20.10)") "cellsize", csize
        write(11,"(a12, i10)") "NODATA_value", -9999
        do i=imin, imax
            write(11,'(10000(i6))') (masked_data(i,j), j=jmin, jmax)
        end do
        close(11)

		deallocate(masked_data)
    end subroutine


end module
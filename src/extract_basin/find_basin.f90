!**********************************************************************
!
!   Copyright (c) 2021 Kazutake Asahi
!   MIT License : https://opensource.org/licenses/mit-license.php 
!	!DIR�f�[�^�𗘗p�������撊�o
!
!**********************************************************************
	recursive subroutine find_basin(ip0, jp0, curr_dist)
	use m_common
	implicit none
	integer, intent(in) :: ip0, jp0
	real*8, intent(in) :: curr_dist ! add y
	integer :: ip, jp
	real*8 :: new_dist, lat1, lon1, lat2, lon2 ! add
!==================================================	  
! --------> j
! |              6 4	  
! |         32----|----128
! |     16--------|--------1	  
! |          8----|----2
! |               4
! ��
! i
	
	! Copyright (c) 2024 yama-k-0129
    ! Set current distance for this cell
    distance(ip0,jp0) = curr_dist
	! Calculate base coordinates for current cell
    lat1 = yl + csize * (ni - ip0)
    lon1 = xl + csize * (jp0 - 1)

	
	!id = 1
	ip = ip0; jp = jp0+1
	if((ip > 1 .and. ip < ni) .and. (jp > 1 .and. jp < nj)) then
		if(idir(ip,jp) == 16) then
			! calculate distance add yama
			lat2 = yl + csize * (ni - ip)
            lon2 = xl + csize * jp
            new_dist = curr_dist + calc_planar_distance(lat1, lon1, lat2, lon2)

			!ibasin(ip,jp) = 16
			ibasin(ip,jp) = 1
			call find_basin(ip, jp, new_dist)
		end if
	end if
		
	!id = 2
	ip = ip0+1; jp = jp0+1
	if((ip > 1 .and. ip < ni) .and. (jp > 1 .and. jp < nj)) then
		if(idir(ip,jp) == 32) then
			! calculate distance
			lat2 = yl + csize * (ni - ip)
            lon2 = xl + csize * jp
            new_dist = curr_dist + calc_planar_distance(lat1, lon1, lat2, lon2)	
			!ibasin(ip,jp) = 32
			ibasin(ip,jp) = 1
			call find_basin(ip, jp, new_dist)
		end if
	end if
	  
	!id = 4
	ip = ip0+1; jp = jp0
	if((ip > 1 .and. ip < ni) .and. (jp > 1 .and. jp < nj)) then
		if(idir(ip,jp) == 64) then
			! calculate distance
			lat2 = yl + csize * (ni - ip)
            lon2 = xl + csize * jp
            new_dist = curr_dist + calc_planar_distance(lat1, lon1, lat2, lon2)	
			!ibasin(ip,jp) = 64
			ibasin(ip,jp) = 1
			call find_basin(ip, jp, new_dist)
		end if
	end if
		
	!id = 8
	ip = ip0+1; jp = jp0-1
	if((ip > 1 .and. ip < ni) .and. (jp > 1 .and. jp < nj)) then
		if(idir(ip,jp) == 128) then
			! calculate distance
			lat2 = yl + csize * (ni - ip)
            lon2 = xl + csize * jp
            new_dist = curr_dist + calc_planar_distance(lat1, lon1, lat2, lon2)	
			!ibasin(ip,jp) = 128
			ibasin(ip,jp) = 1
			call find_basin(ip, jp, new_dist)
		end if
	end if

	!id = 16
	ip = ip0; jp = jp0-1
	if((ip > 1 .and. ip < ni) .and. (jp > 1 .and. jp < nj)) then
		if(idir(ip,jp) == 1) then
			! calculate distance
			lat2 = yl + csize * (ni - ip)
            lon2 = xl + csize * jp
            new_dist = curr_dist + calc_planar_distance(lat1, lon1, lat2, lon2)	
			ibasin(ip,jp) = 1
			call find_basin(ip, jp, new_dist)
		end if
	end if
	!id = 32
	ip = ip0-1; jp = jp0-1
	if((ip > 1 .and. ip < ni) .and. (jp > 1 .and. jp < nj)) then
		if(idir(ip,jp) == 2) then
			! calculate distance
			lat2 = yl + csize * (ni - ip)
            lon2 = xl + csize * jp
            new_dist = curr_dist + calc_planar_distance(lat1, lon1, lat2, lon2)	
			!ibasin(ip,jp) = 2
			ibasin(ip,jp) = 1
			call find_basin(ip, jp, new_dist)
		end if
	end if
	!id = 64
	ip = ip0-1; jp = jp0
	if((ip > 1 .and. ip < ni) .and. (jp > 1 .and. jp < nj)) then
		if(idir(ip,jp) == 4) then
			! calculate distance
			lat2 = yl + csize * (ni - ip)
            lon2 = xl + csize * jp
            new_dist = curr_dist + calc_planar_distance(lat1, lon1, lat2, lon2)
			!ibasin(ip,jp) = 4
			ibasin(ip,jp) = 1
			call find_basin(ip, jp, new_dist)
		end if
	end if
		
	!id = 128
	ip = ip0-1; jp = jp0+1
	if((ip > 1 .and. ip < ni) .and. (jp > 1 .and. jp < nj)) then
		if(idir(ip,jp) == 8) then
			! calculate distance
			lat2 = yl + csize * (ni - ip)
            lon2 = xl + csize * jp
            new_dist = curr_dist + calc_planar_distance(lat1, lon1, lat2, lon2)
			!ibasin(ip,jp) = 8
			ibasin(ip,jp) = 1
			call find_basin(ip, jp, new_dist)
		end if
	end if
	return
	end subroutine
/*
 * Copyright (C) 2012 Niek Linnenbank
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef __LIB_DUMMY_H
#define __LIB_DUMMY_H

/* #include <FreeNOS/config.h> */
/* #ifdef CONFIG_UTIL_STUFF */

extern int util_same(int param);
extern int util_multiply(int param);
extern int util_add(int param1, int param2);

/* #endif CONFIG_UTIL_STUFF */

extern int lookup_string(char *param);
extern int lookup_int(int param);

#endif /* __LIB_DUMMY_H */

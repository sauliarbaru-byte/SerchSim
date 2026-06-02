 Garis Lintang

/* ====================== KONSTANTA DAN TIPE DATA ====================== */
KONSTANTA
    COLS ← 20                       // jumlah kolom grid
    ROWS ← 15                       // jumlah baris grid
    CELL_SIZE ← 30                  // ukuran sel dalam piksel
    k ← 2.5                         // bobot penalti simpangan garis lurus

TIPE
    Point ← RECORD
        x, y : REAL
    ENDRECORD
    Cell ← RECORD
        col, row : INTEGER
    ENDRECORD

/* ====================== VARIABEL GLOBAL ====================== */
VAR
    grid : ARRAY[0..ROWS-1][0..COLS-1] OF INTEGER   // 0 = kosong, 1 = rintangan
    startCell, goalCell : Cell

/* ====================== FUNGSI BANTU GEOMETRI ====================== */
FUNCTION CellCenter(c : Cell) : Point
    // mengembalikan koordinat tengah sel dalam piksel
    RETURN Point(c.col * CELL_SIZE + CELL_SIZE/2,
                 c.row * CELL_SIZE + CELL_SIZE/2)
END FUNCTION

FUNCTION EuclideanDistance(P, Q : Point) : REAL
    RETURN SQRT((P.x - Q.x)^2 + (P.y - Q.y)^2)
END FUNCTION

FUNCTION PerpendicularDistance(P : Point, A, B : Point) : REAL
    // jarak titik P ke garis lurus tak hingga yang melalui A dan B
    dx ← B.x - A.x
    dy ← B.y - A.y
    IF dx = 0 AND dy = 0 THEN
        RETURN EuclideanDistance(P, A)
    ENDIF
    cross ← ABS(dx * (A.y - P.y) - (A.x - P.x) * dy)
    RETURN cross / SQRT(dx^2 + dy^2)
END FUNCTION

/* ====================== DETEKSI TABRAKAN GARIS LURUS ====================== */
FUNCTION GetLineCollisions(A, B : Cell) : LIST OF Cell
    // mengembalikan semua sel rintangan yang dilalui garis lurus A–B
    startPoint ← CellCenter(A)
    endPoint   ← CellCenter(B)
    totalDist ← EuclideanDistance(startPoint, endPoint)
    stepCount ← MAX(200, CEIL(totalDist / 2))   // sampling cukup rapat
    collisions ← empty list

    FOR i ← 0 TO stepCount DO
        t ← i / stepCount
        x ← startPoint.x + t * (endPoint.x - startPoint.x)
        y ← startPoint.y + t * (endPoint.y - startPoint.y)
        col ← FLOOR(x / CELL_SIZE)
        row ← FLOOR(y / CELL_SIZE)
        IF col >= 0 AND col < COLS AND row >= 0 AND row < ROWS THEN
            IF grid[row][col] = 1 THEN
                // tambahkan jika belum ada di collisions
                IF NOT CONTAINS(collisions, Cell(col, row)) THEN
                    collisions.APPEND(Cell(col, row))
                ENDIF
            ENDIF
        ENDIF
    ENDFOR
    RETURN collisions
END FUNCTION

/* ====================== PERHITUNGAN SKOR PRIORITAS ====================== */
FUNCTION CalculateScore(candidate : Cell, goal : Cell, lineStart, lineEnd : Point) : REAL
    cCenter ← CellCenter(candidate)
    gCenter ← CellCenter(goal)
    D_goal ← EuclideanDistance(cCenter, gCenter) / CELL_SIZE   // dalam satuan grid
    T      ← PerpendicularDistance(cCenter, lineStart, lineEnd) / CELL_SIZE
    RETURN D_goal + k * T
END FUNCTION

/* ====================== MENDAPATKAN TETANGGA ====================== */
FUNCTION GetNeighbors(c : Cell) : LIST OF Cell
    neighbors ← empty list
    FOR dcol FROM -1 TO 1 DO
        FOR drow FROM -1 TO 1 DO
            IF dcol = 0 AND drow = 0 THEN CONTINUE
            nc ← c.col + dcol
            nr ← c.row + drow
            IF nc >= 0 AND nc < COLS AND nr >= 0 AND nr < ROWS THEN
                IF grid[nr][nc] = 0 THEN            // bukan rintangan
                    neighbors.APPEND(Cell(nc, nr))
                ENDIF
            ENDIF
        ENDFOR
    ENDFOR
    // goalCell juga bisa menjadi tetangga meskipun mungkin bukan "kosong" (dianggap selalu bisa)
    RETURN neighbors
END FUNCTION

/* ====================== ALGORITMA PENCARIAN JALUR ====================== */
FUNCTION FindPath(start, goal : Cell) : LIST OF Cell
    // antrian prioritas diimplementasikan dengan min‑heap berdasarkan skor
    frontier ← EMPTY_MIN_PRIORITY_QUEUE()
    startScore ← CalculateScore(start, goal, CellCenter(start), CellCenter(goal))
    frontier.ENQUEUE(start, startScore)

    came_from ← EMPTY DICTIONARY   // memetakan Cell → Cell (asal)
    explored ← EMPTY SET
    frontier_set ← EMPTY SET       // untuk pengecekan keanggotaan cepat
    frontier_set.INSERT(start)
    came_from[start] ← NULL

    WHILE NOT frontier.IS_EMPTY() DO
        current ← frontier.DEQUEUE()   // sel dengan skor terkecil
        frontier_set.REMOVE(current)

        IF current = goal THEN
            RETURN ReconstructPath(came_from, current)
        ENDIF

        explored.INSERT(current)

        FOR EACH neighbor IN GetNeighbors(current) DO
            IF explored.CONTAINS(neighbor) THEN CONTINUE
            IF frontier_set.CONTAINS(neighbor) THEN CONTINUE   // tidak update skor

            newScore ← CalculateScore(neighbor, goal,
                                      CellCenter(start), CellCenter(goal))
            frontier.ENQUEUE(neighbor, newScore)
            frontier_set.INSERT(neighbor)
            came_from[neighbor] ← current
        ENDFOR
    ENDWHILE

    RETURN NULL   // jalur tidak ditemukan
END FUNCTION

FUNCTION ReconstructPath(came_from : DICTIONARY, current : Cell) : LIST OF Cell
    path ← EMPTY LIST
    WHILE current != NULL DO
        path.PREPEND(current)
        current ← came_from[current]
    ENDWHILE
    RETURN path
END FUNCTION

/* ====================== PROGRAM UTAMA ====================== */
PROCEDURE Main()
    // 1. Inisialisasi grid (contoh: beberapa rintangan)
    FOR r ← 0 TO ROWS-1 DO
        FOR c ← 0 TO COLS-1 DO
            grid[r][c] ← 0
        ENDFOR
    ENDFOR
    // Tambahkan rintangan contoh (dinding vertikal dengan celah)
    // ... (disesuaikan kebutuhan)

    // 2. Tentukan titik awal dan tujuan
    startCell ← Cell(2, 7)
    goalCell  ← Cell(17, 7)

    // 3. Tampilkan hasil deteksi tabrakan garis lurus
    collisions ← GetLineCollisions(startCell, goalCell)
    IF LENGTH(collisions) > 0 THEN
        OUTPUT "Garis lurus terhalang oleh " + LENGTH(collisions) + " rintangan."
    ELSE
        OUTPUT "Garis lurus bebas rintangan."
    ENDIF

    // 4. Lakukan pencarian jalur
    path ← FindPath(startCell, goalCell)
    IF path = NULL THEN
        OUTPUT "Tidak ada jalur yang ditemukan."
    ELSE
        OUTPUT "Jalur ditemukan dengan " + LENGTH(path) + " langkah:"
        FOR EACH cell IN path DO
            OUTPUT "  (" + cell.col + "," + cell.row + ")"
        ENDFOR
    ENDIF
END PROCEDURE

// Jalankan program utama
CALL Main()
END PROGRAM
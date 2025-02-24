CREATE TABLE IF NOT EXISTS diff (
    diffid BIGINT PRIMARY KEY,
    procid BIGINT,
    expid BIGINT,
    rawpath VARCHAR(255),
    savepath VARCHAR(255),
    DIFFPSF VARCHAR(255),
    DIFFSCR VARCHAR(255),
    DIFFUNC VARCHAR(255),
    OBSDATE INT,
    timeutc TIMESTAMPTZ,
    FILTER VARCHAR(10),
    EXPTIME REAL,
    NIGHT INT,
    fieldID INT,
    CENTRA REAL,
    CENTDEC REAL,
    ZP_AUTO REAL,
    SCORSTD REAL,
    SCORMED REAL,
    SCORMEAN REAL,
    DIFFMLIM REAL,
    diffcount SERIAL,
    CONSTRAINT fk_expid
            FOREIGN KEY(expid)
                REFERENCES raw(expid),
    CONSTRAINT fk_procid
            FOREIGN KEY(procid)
                REFERENCES proc(procid)
);

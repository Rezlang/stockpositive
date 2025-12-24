CREATE TABLE usergroup_permissions (
    usergroup_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    permission_value INTEGER,

    CONSTRAINT pk_usergroup_permissions
        PRIMARY KEY (usergroup_id, permission_id),

    CONSTRAINT fk_usergroup_permissions_usergroup
        FOREIGN KEY (usergroup_id)
        REFERENCES usergroups(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_usergroup_permissions_permission
        FOREIGN KEY (permission_id)
        REFERENCES permissions(id)
        ON DELETE CASCADE
);

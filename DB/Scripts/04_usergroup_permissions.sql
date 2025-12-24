CREATE TABLE usergroup_permissions (
    id SERIAL PRIMARY KEY,
    usergroup_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    CONSTRAINT fk_usergroup_permissions_usergroup
        FOREIGN KEY (usergroup_id)
        REFERENCES usergroups(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_usergroup_permissions_permission
        FOREIGN KEY (permission_id)
        REFERENCES permissions(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_usergroup_permission UNIQUE (usergroup_id, permission_id)
);

CREATE INDEX idx_usergroup_permissions_usergroup ON usergroup_permissions(usergroup_id);
CREATE INDEX idx_usergroup_permissions_permission ON usergroup_permissions(permission_id);
-- admin has all permissions
INSERT INTO usergroup_permissions (usergroup_id, permission_id)
SELECT ug.id, p.id
FROM usergroups ug
JOIN permissions p ON ug.name = 'admin';

-- user has read only
INSERT INTO usergroup_permissions (usergroup_id, permission_id)
SELECT ug.id, p.id
FROM usergroups ug
JOIN permissions p ON ug.name = 'user' AND p.name = 'GET.NEWS';

INSERT INTO usergroup_permissions (usergroup_id, permission_id)
SELECT ug.id, p.id
FROM usergroups ug
JOIN permissions p ON ug.name = 'user' AND p.name = 'WRITE.FEED.5';

INSERT INTO usergroup_permissions (usergroup_id, permission_id)
SELECT ug.id, p.id
FROM usergroups ug
JOIN permissions p ON ug.name = 'free' AND p.name = 'GET.NEWS';

INSERT INTO usergroup_permissions (usergroup_id, permission_id)
SELECT ug.id, p.id
FROM usergroups ug
JOIN permissions p ON ug.name = 'free' AND p.name = 'WRITE.FEED.2';
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
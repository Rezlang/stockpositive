-- Admin permissions
INSERT INTO usergroup_permissions (usergroup_id, permission_id, permission_value)
SELECT ug.id, p.id,
       CASE p.name
           WHEN 'ADD.FEED' THEN -2
           ELSE -1
       END
FROM usergroups ug
JOIN permissions p
  ON ug.name = 'admin';

-- User permissions
INSERT INTO usergroup_permissions (usergroup_id, permission_id, permission_value)
SELECT ug.id, p.id,
       CASE p.name
           WHEN 'GET.NEWS' THEN -1
           WHEN 'GET.FEEDS' THEN -1
           WHEN 'ADD.FEED' THEN 5
           WHEN 'EDIT.FEED' THEN -1
           WHEN 'DELETE.FEED' THEN -1
           ELSE NULL
       END
FROM usergroups ug
JOIN permissions p
  ON ug.name = 'user'
WHERE p.name IN ('GET.NEWS', 'GET.FEEDS', 'ADD.FEED', 'EDIT.FEED', 'DELETE.FEED');

-- Free permissions
INSERT INTO usergroup_permissions (usergroup_id, permission_id, permission_value)
SELECT ug.id, p.id,
       CASE p.name
           WHEN 'GET.NEWS' THEN -1
           WHEN 'GET.FEEDS' THEN -1
           WHEN 'ADD.FEED' THEN 2
           WHEN 'EDIT.FEED' THEN -1
           WHEN 'DELETE.FEED' THEN -1
           ELSE NULL
       END
FROM usergroups ug
JOIN permissions p
  ON ug.name = 'free'
WHERE p.name IN ('GET.NEWS', 'GET.FEEDS', 'ADD.FEED', 'EDIT.FEED', 'DELETE.FEED');

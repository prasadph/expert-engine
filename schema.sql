SET FOREIGN_KEY_CHECKS=0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

CREATE DATABASE IF NOT EXISTS `discussionforum` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `discussionforum`;

CREATE TABLE `comments` (
  `id` int(11) NOT NULL,
  `text` varchar(45) DEFAULT NULL,
  `threads_id` int(11) NOT NULL,
  `users_id` int(11) NOT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `blocked` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `groups` (
  `id` int(11) NOT NULL,
  `name` varchar(45) NOT NULL,
  `admin` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `tags` (
  `id` int(11) NOT NULL,
  `name` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `tags_has_threads` (
  `tags_id` int(11) NOT NULL,
  `threads_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `threads` (
  `id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `content` varchar(1000) NOT NULL,
  `users_id` int(11) NOT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `groups_id` int(11) DEFAULT NULL,
  `blocked` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `email` varchar(45) NOT NULL,
  `fname` varchar(45) NOT NULL,
  `lname` varchar(45) NOT NULL,
  `password` varchar(45) NOT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `login` datetime DEFAULT NULL,
  `role` varchar(5) DEFAULT 'basic'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `users_has_groups` (
  `users_id` int(11) NOT NULL,
  `groups_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


ALTER TABLE `comments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_comments_threads1_idx` (`threads_id`),
  ADD KEY `fk_comments_users1_idx` (`users_id`);

ALTER TABLE `groups`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_group_users1_idx` (`admin`);

ALTER TABLE `tags`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name_UNIQUE` (`name`);

ALTER TABLE `tags_has_threads`
  ADD PRIMARY KEY (`tags_id`,`threads_id`),
  ADD KEY `fk_tags_has_threads_threads1_idx` (`threads_id`),
  ADD KEY `fk_tags_has_threads_tags1_idx` (`tags_id`);

ALTER TABLE `threads`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_threads_users_idx` (`users_id`),
  ADD KEY `fk_threads_group1_idx` (`groups_id`);

ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email_UNIQUE` (`email`);

ALTER TABLE `users_has_groups`
  ADD PRIMARY KEY (`users_id`,`groups_id`),
  ADD KEY `fk_users_has_group_group1_idx` (`groups_id`),
  ADD KEY `fk_users_has_group_users1_idx` (`users_id`);


ALTER TABLE `comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
ALTER TABLE `groups`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
ALTER TABLE `tags`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
ALTER TABLE `threads`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `comments`
  ADD CONSTRAINT `fk_comments_threads1` FOREIGN KEY (`threads_id`) REFERENCES `threads` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_comments_users1` FOREIGN KEY (`users_id`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `groups`
  ADD CONSTRAINT `fk_group_users1` FOREIGN KEY (`admin`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `tags_has_threads`
  ADD CONSTRAINT `fk_tags_has_threads_tags1` FOREIGN KEY (`tags_id`) REFERENCES `tags` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_tags_has_threads_threads1` FOREIGN KEY (`threads_id`) REFERENCES `threads` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `threads`
  ADD CONSTRAINT `fk_threads_group1` FOREIGN KEY (`groups_id`) REFERENCES `groups` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_threads_users` FOREIGN KEY (`users_id`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `users_has_groups`
  ADD CONSTRAINT `fk_users_has_group_group1` FOREIGN KEY (`groups_id`) REFERENCES `groups` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_users_has_group_users1` FOREIGN KEY (`users_id`) REFERENCES `users` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
SET FOREIGN_KEY_CHECKS=1;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

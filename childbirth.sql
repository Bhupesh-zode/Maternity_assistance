-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Mar 13, 2023 at 11:53 AM
-- Server version: 8.0.31
-- PHP Version: 8.0.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `childbirth`
--
CREATE DATABASE IF NOT EXISTS `childbirth` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `childbirth`;

-- --------------------------------------------------------

--
-- Table structure for table `algorithms_details`
--

DROP TABLE IF EXISTS `algorithms_details`;
CREATE TABLE IF NOT EXISTS `algorithms_details` (
  `algo_id` int NOT NULL AUTO_INCREMENT,
  `algo_name` varchar(100) DEFAULT NULL,
  `accuracy` varchar(500) DEFAULT NULL,
  `precision` varchar(500) DEFAULT NULL,
  `recall` varchar(500) DEFAULT NULL,
  `f1_score` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`algo_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `algorithms_details`
--

INSERT INTO `algorithms_details` (`algo_id`, `algo_name`, `accuracy`, `precision`, `recall`, `f1_score`) VALUES
(3, 'xgboost', '0.8355437665782494', '0.7219343614499791', '0.8069273539330963', '0.7540548051143245'),
(2, 'logisticregression', '0.6816976127320955', '0.6999490115165038', '0.5639526337280523', '0.5768266983035761'),
(4, 'gradientboostingclassifier', '0.7877984084880637', '0.721016658660613', '0.7369463869463869', '0.7129029840979676');

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE IF NOT EXISTS `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_group_id_b120cbf9` (`group_id`),
  KEY `auth_group_permissions_permission_id_84c5c92e` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  KEY `auth_permission_content_type_id_2f476e4b` (`content_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=37 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add user', 4, 'add_user'),
(14, 'Can change user', 4, 'change_user'),
(15, 'Can delete user', 4, 'delete_user'),
(16, 'Can view user', 4, 'view_user'),
(17, 'Can add content type', 5, 'add_contenttype'),
(18, 'Can change content type', 5, 'change_contenttype'),
(19, 'Can delete content type', 5, 'delete_contenttype'),
(20, 'Can view content type', 5, 'view_contenttype'),
(21, 'Can add session', 6, 'add_session'),
(22, 'Can change session', 6, 'change_session'),
(23, 'Can delete session', 6, 'delete_session'),
(24, 'Can view session', 6, 'view_session'),
(25, 'Can add main model', 7, 'add_mainmodel'),
(26, 'Can change main model', 7, 'change_mainmodel'),
(27, 'Can delete main model', 7, 'delete_mainmodel'),
(28, 'Can view main model', 7, 'view_mainmodel'),
(29, 'Can add dataset', 8, 'add_dataset'),
(30, 'Can change dataset', 8, 'change_dataset'),
(31, 'Can delete dataset', 8, 'delete_dataset'),
(32, 'Can view dataset', 8, 'view_dataset'),
(33, 'Can add algorithms', 9, 'add_algorithms'),
(34, 'Can change algorithms', 9, 'change_algorithms'),
(35, 'Can delete algorithms', 9, 'delete_algorithms'),
(36, 'Can view algorithms', 9, 'view_algorithms');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
CREATE TABLE IF NOT EXISTS `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE IF NOT EXISTS `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_user_id_6a12ed8b` (`user_id`),
  KEY `auth_user_groups_group_id_97559544` (`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
CREATE TABLE IF NOT EXISTS `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_user_id_a95ead1b` (`user_id`),
  KEY `auth_user_user_permissions_permission_id_1fbb5f2c` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `dataset_file_info`
--

DROP TABLE IF EXISTS `dataset_file_info`;
CREATE TABLE IF NOT EXISTS `dataset_file_info` (
  `data_id` int NOT NULL AUTO_INCREMENT,
  `data_set` varchar(100) NOT NULL,
  PRIMARY KEY (`data_id`)
) ENGINE=MyISAM AUTO_INCREMENT=20 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `dataset_file_info`
--

INSERT INTO `dataset_file_info` (`data_id`, `data_set`) VALUES
(1, 'dataset/childbirth.csv'),
(2, 'dataset/childbirth_nxtvZIh.csv'),
(3, 'dataset/childbirth_U1YJ2lP.csv'),
(4, 'dataset/childbirth_XkCozmV.csv'),
(5, 'dataset/childbirth_aQZArBs.csv'),
(6, 'dataset/childbirth_AfBlfXC.csv'),
(7, 'dataset/childbirth_RmCSqo0.csv'),
(8, 'dataset/childbirth_PJY3WBw.csv'),
(9, 'dataset/childbirth1.csv'),
(10, 'dataset/childbirth1_MnSiiiv.csv'),
(11, 'dataset/childbirth1_BuZw0Nk.csv'),
(12, 'dataset/childbirth2.csv'),
(13, 'dataset/childbirth2_yA2Nl5L.csv'),
(14, 'dataset/childbirth2_VqyEuxr.csv'),
(15, 'dataset/childbirth2_Nc3qVeu.csv'),
(16, 'dataset/childbirth2_4FAeh5W.csv'),
(17, 'dataset/childbirth2_nXyo7we.csv'),
(18, 'dataset/childbirth2_mTJ0HMB.csv'),
(19, 'dataset/childbirth2_ImxmomT.csv');

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE IF NOT EXISTS `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint UNSIGNED NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(2, 'auth', 'permission'),
(3, 'auth', 'group'),
(4, 'auth', 'user'),
(5, 'contenttypes', 'contenttype'),
(6, 'sessions', 'session'),
(7, 'mainapp', 'mainmodel'),
(8, 'adminapp', 'dataset'),
(9, 'adminapp', 'algorithms');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE IF NOT EXISTS `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=29 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2023-03-06 11:18:06.380868'),
(2, 'auth', '0001_initial', '2023-03-06 11:18:06.710621'),
(3, 'admin', '0001_initial', '2023-03-06 11:18:06.796101'),
(4, 'admin', '0002_logentry_remove_auto_add', '2023-03-06 11:18:06.814594'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2023-03-06 11:18:06.832275'),
(6, 'contenttypes', '0002_remove_content_type_name', '2023-03-06 11:18:06.902006'),
(7, 'auth', '0002_alter_permission_name_max_length', '2023-03-06 11:18:06.930867'),
(8, 'auth', '0003_alter_user_email_max_length', '2023-03-06 11:18:06.973296'),
(9, 'auth', '0004_alter_user_username_opts', '2023-03-06 11:18:06.984201'),
(10, 'auth', '0005_alter_user_last_login_null', '2023-03-06 11:18:07.035475'),
(11, 'auth', '0006_require_contenttypes_0002', '2023-03-06 11:18:07.039913'),
(12, 'auth', '0007_alter_validators_add_error_messages', '2023-03-06 11:18:07.066159'),
(13, 'auth', '0008_alter_user_username_max_length', '2023-03-06 11:18:07.103674'),
(14, 'auth', '0009_alter_user_last_name_max_length', '2023-03-06 11:18:07.145532'),
(15, 'auth', '0010_alter_group_name_max_length', '2023-03-06 11:18:07.187403'),
(16, 'auth', '0011_update_proxy_permissions', '2023-03-06 11:18:07.216242'),
(17, 'auth', '0012_alter_user_first_name_max_length', '2023-03-06 11:18:07.250659'),
(18, 'mainapp', '0001_initial', '2023-03-06 11:18:07.270311'),
(19, 'mainapp', '0002_alter_mainmodel_table', '2023-03-06 11:18:07.285754'),
(20, 'mainapp', '0003_alter_mainmodel_image', '2023-03-06 11:18:07.300432'),
(21, 'sessions', '0001_initial', '2023-03-06 11:18:07.331552'),
(22, 'userapp', '0001_initial', '2023-03-06 11:18:07.353591'),
(23, 'userapp', '0002_delete_usermodel', '2023-03-06 11:18:07.369606'),
(24, 'adminapp', '0001_initial', '2023-03-06 11:33:13.842991'),
(25, 'adminapp', '0002_dataset_accuracy_dataset_f1_score_dataset_model_name_and_more', '2023-03-10 08:06:44.024999'),
(26, 'adminapp', '0003_remove_dataset_accuracy_remove_dataset_f1_score_and_more', '2023-03-10 08:34:25.690874'),
(27, 'adminapp', '0004_algorithms', '2023-03-10 08:38:29.289685'),
(28, 'mainapp', '0004_mainmodel_status', '2023-03-13 06:17:44.598544');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('ofjd46o4yhollo2a7wnjt8f579cr069k', 'eyJzbm8iOjF9:1pbb2f:Chgz5m27ttCi20bhARomdCbubyRUnRpLQ5Qid_zHbvA', '2023-03-27 05:48:17.182593'),
('wb1zj9q4iqmhaq0g6uf7vmzp2titfq70', 'eyJzbm8iOjF9:1paz8e:XebxB5hvtUAmdSHWWvKW0FUoKhQG3SDNzRf0oqrWh4U', '2023-03-25 13:19:56.772123'),
('398e2khoijcj8f26fpkc9fjs2i5m6l6m', 'eyJzbm8iOjJ9:1pbgW4:CdZ3kMn1h6ItDPj56ws8ksO2dBpDlHwF80sbZlVjPK4', '2023-03-27 11:39:00.173477');

-- --------------------------------------------------------

--
-- Table structure for table `user details`
--

DROP TABLE IF EXISTS `user details`;
CREATE TABLE IF NOT EXISTS `user details` (
  `sno` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `email` varchar(254) NOT NULL,
  `Phone Number` varchar(11) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `relation` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL,
  `image` varchar(100) NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`sno`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user details`
--

INSERT INTO `user details` (`sno`, `name`, `email`, `Phone Number`, `address`, `relation`, `password`, `image`, `status`) VALUES
(1, 'harsh', 'admin@gmail.com', '8770600877', '', 'Self', '1234', 'media/user/Screenshot_1.png', 'accepted'),
(2, 'marnu', 'marnus@gmail.com', '8596741523', 'Hyderabad', 'Self', 'Ma12346', 'media/user/man1.jpg', 'restricted'),
(3, 'deepika', 'deepika@gmail.com', '7895684213', 'Mumbai', 'Self', 'Dee258369', 'media/user/woman3.jpg', 'accepted');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

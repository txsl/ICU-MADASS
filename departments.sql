-- phpMyAdmin SQL Dump
-- version 3.5.3
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Sep 17, 2014 at 10:55 PM
-- Server version: 5.1.73
-- PHP Version: 5.3.3

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `mumsanddads`
--

-- --------------------------------------------------------

--
-- Table structure for table `Departments`
--

CREATE TABLE IF NOT EXISTS `Departments` (
  `DepartmentId` int(11) NOT NULL AUTO_INCREMENT,
  `DepartmentName` varchar(200) NOT NULL,
  `DepartmentNameTypeName` varchar(200) NOT NULL,
  `ParentsNeeded` int(11) DEFAULT NULL,
  `FreshersNeeded` int(11) DEFAULT NULL,
  `SocietyName` varchar(200) NOT NULL,
  `ShowPicture` tinyint(1) NOT NULL DEFAULT '1',
  `Email` varchar(150) NOT NULL,
  `Webpage` varchar(300) NOT NULL,
  `Facebook` varchar(300) NOT NULL,
  `FreshersGroup` varchar(300) NOT NULL,
  `OptedOut` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`DepartmentId`),
  UNIQUE KEY `DepartmentName` (`DepartmentName`,`DepartmentNameTypeName`),
  KEY `DepartmentNameTypeName` (`DepartmentNameTypeName`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=20 ;

--
-- Dumping data for table `Departments`
--

INSERT INTO `Departments` (`DepartmentId`, `DepartmentName`, `DepartmentNameTypeName`, `ParentsNeeded`, `FreshersNeeded`, `SocietyName`, `ShowPicture`, `Email`, `Webpage`, `Facebook`, `FreshersGroup`, `OptedOut`) VALUES
(4, 'Department of Mechanical Engineering', 'Mechanical Engineering', 80, 167, 'MechSoc', 1, 'mechsoc@imperial.ac.uk', 'https://www.union.ic.ac.uk/guilds/mechsoc/', '', 'https://www.facebook.com/groups/691955964214414/', 0),
(5, 'Department of Bioengineering', 'Bioengineering', 50, 97, 'Bioengineering Society', 1, 'bioengsoc@imperial.ac.uk', 'http://www.union.ic.ac.uk/guilds/bioeng', 'https://www.facebook.com/groups/490568677744751/', '', 0),
(6, 'Department of Aeronautics', 'Aeronautics', 56, 110, 'Aeronautical Society', 1, 'aerosoc@imperial.ac.uk', 'http://www.union.ic.ac.uk/guilds/aero', '', '', 1),
(7, 'Departments of Computing: Computing and JMC', 'JMC & Computing', 84, 165, 'DOC SOC', 1, 'docsoc@imperial.ac.uk', 'http://www.union.ic.ac.uk/guilds/docsoc', '', 'www.facebook.com/groups/iccomputing2014/', 0),
(8, 'Department of Chemistry', 'Chemistry', 94, 186, 'ChemSoc', 1, 'rcsu.chem@imperial.ac.uk', 'http://rcsu.org.uk/chemsoc', '', 'https://www.facebook.com/groups/680831831965825/', 0),
(9, 'Department of Civil & Environmental Engineering', 'Civil & Environmental Engineering', 50, 98, 'CIVSOC', 1, 'civsoc@imperial.ac.uk', 'http://www.union.ic.ac.uk/guilds/civsoc', '', 'https://www.facebook.com/groups/471628099641194/', 0),
(10, 'Department of Earth Science & Engineering', 'Earth Science & Engineering', 44, 85, 'Royal School of Mines Union', 1, 'rsm.president@imperial.ac.uk', 'http://union.ic.ac.uk/rsm', '', 'https://www.facebook.com/groups/260041587537605/', 0),
(11, 'Department of Mathematics', 'Mathematics', 114, 227, 'Mathsoc', 1, 'mathssoc@imperial.ac.uk', 'http://www.union.ic.ac.uk/rcsu/mathsoc', '', 'https://www.facebook.com/groups/ImperialMathematics2014/', 0),
(12, 'Department of Life Sciences: Biochemistry and Biotechnology', 'Biochemistry', 80, 159, 'icbiochem', 1, 'biochemsoc@imperial.ac.uk', 'http://union.ic.ac.uk/rcsu/biochem', '', 'https://www.facebook.com/groups/BiochemFreshers2014/', 0),
(13, 'Department of Physics', 'Physics', 124, 247, 'PhySoc', 1, 'physics.society@imperial.ac.uk', 'http://www.union.ic.ac.uk/rcsu/physoc', '', 'https://www.facebook.com/groups/248708351982571/', 0),
(14, 'Department of Life Sciences: Biology, Ecology, Microbiology, and Zoology', 'Biology', 72, 143, 'BioSoc', 1, 'biosoc@imperial.ac.uk', 'http://www.facebook.com/groups/ImperialBioSoc/', '', 'https://www.facebook.com/groups/625333544252345/', 0),
(16, 'Department of Electrical & Electronic Engineering: Electrical & Electronic Engineering and Electronic & Information Engineering', 'Electrical & Electronic Engineering', 100, 198, 'EESoc', 1, 'eesoc@imperial.ac.uk', 'http://www.cgcu.net/eesoc/', '', 'https://www.facebook.com/groups/1405821563024185/', 0),
(17, 'Department of Materials', 'Materials', 62, 122, 'Imperial Materials', 1, 'mtsoc@imperial.ac.uk', 'http://www.union.ic.ac.uk/rsm/matsoc', '', 'https://www.facebook.com/groups/materials2014/', 0),
(18, 'Faculty of Medicine', 'Medicine', 0, 0, 'Imperial College School of Medicine Students'' Union', 0, 'icsm.president@imperial.ac.uk', 'http://www.icsmsu.com/', '', '', 1),
(19, 'Department of Chemical Engineering', 'Chemical Engineering', 66, 132, 'ChemEngSoc', 1, 'chemengsoc@imperial.ac.uk', 'http://www.union.ic.ac.uk/guilds/chemeng', '', 'https://www.facebook.com/groups/imperialchemeng18/', 0);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

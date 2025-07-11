/*
Navicat MySQL Data Transfer

Source Server         : localhost_3306
Source Server Version : 50740
Source Host           : localhost:3306
Source Database       : carrent928

Target Server Type    : MYSQL
Target Server Version : 50740
File Encoding         : 65001

Date: 2025-05-29 14:27:23
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for cars
-- ----------------------------
DROP TABLE IF EXISTS `cars`;
CREATE TABLE `cars` (
  `CarID` int(11) NOT NULL AUTO_INCREMENT,
  `CarName` char(10) NOT NULL,
  `CarMoney` double(20,2) DEFAULT '0.00',
  `CarType` char(30) NOT NULL,
  `CarRent` enum('是','否') DEFAULT NULL,
  `userId` int(11) DEFAULT NULL,
  PRIMARY KEY (`CarID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of cars
-- ----------------------------
INSERT INTO `cars` VALUES ('2', 'we', '123.00', '2', '是', '20');

-- ----------------------------
-- Table structure for managers
-- ----------------------------
DROP TABLE IF EXISTS `managers`;
CREATE TABLE `managers` (
  `manageId` int(11) NOT NULL AUTO_INCREMENT,
  `manageName` char(10) NOT NULL,
  `managePassword` char(50) DEFAULT NULL,
  PRIMARY KEY (`manageId`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of managers
-- ----------------------------
INSERT INTO `managers` VALUES ('2', 'we', '202cb962ac59075b964b07152d234b70');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `userId` int(11) NOT NULL AUTO_INCREMENT,
  `userName` char(10) NOT NULL,
  `userPassword` char(50) DEFAULT NULL,
  PRIMARY KEY (`userId`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES ('12', 'ee', '202cb962ac59075b964b07152d234b70');
INSERT INTO `users` VALUES ('14', 'er', '202cb962ac59075b964b07152d234b70');
INSERT INTO `users` VALUES ('16', 'et', '202cb962ac59075b964b07152d234b70');
INSERT INTO `users` VALUES ('17', '123', '202cb962ac59075b964b07152d234b70');
INSERT INTO `users` VALUES ('18', '123', '202cb962ac59075b964b07152d234b70');
INSERT INTO `users` VALUES ('20', 'we', '202cb962ac59075b964b07152d234b70');
INSERT INTO `users` VALUES ('22', 'ed', '81dc9bdb52d04dc20036dbd8313ed055');
INSERT INTO `users` VALUES ('24', 'eg', '827ccb0eea8a706c4c34a16891f84e7b');
INSERT INTO `users` VALUES ('26', 'wer', '81dc9bdb52d04dc20036dbd8313ed055');
INSERT INTO `users` VALUES ('28', 'de', '202cb962ac59075b964b07152d234b70');
INSERT INTO `users` VALUES ('30', 'wee', '202cb962ac59075b964b07152d234b70');
INSERT INTO `users` VALUES ('32', 'wert', '202cb962ac59075b964b07152d234b70');

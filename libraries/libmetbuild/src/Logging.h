
#ifndef METGET_LOGGING_H
#define METGET_LOGGING_H

#include <iostream>
#include <string>

#include "MetBuild_Global.h"

namespace MetBuild {

class Logging {
 public:
  METBUILD_EXPORT Logging() = default;

  static void METBUILD_EXPORT throwError(const std::string &s);
  static void METBUILD_EXPORT throwError(const std::string &s, const char *file,
                                         int line);

  static void METBUILD_EXPORT
  logError(const std::string &s, const std::string &heading = std::string());
  static void METBUILD_EXPORT
  warning(const std::string &s, const std::string &heading = std::string());
  static void METBUILD_EXPORT log(const std::string &s,
                                  const std::string &heading = std::string());

 private:
  static void printMessage(const std::string &header,
                           const std::string &message);
  static void printErrorMessage(const std::string &header,
                                const std::string &message);
};

}  // namespace MetBuild
/**
 * @def metget_throw_exception
 * @brief Throws an exception to the user with the file and line number sources
 * from which the exception was thrown
 * @param arg string describing the error that is being thrown
 */
#define metbuild_throw_exception(arg) \
  MetBuild::Logging::throwError(arg, __FILE__, __LINE__)

#endif  // METGET_LOGGING_H

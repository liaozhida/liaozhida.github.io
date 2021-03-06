package com.test.sample;

import org.assertj.core.api.Assertions;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.junit4.SpringRunner;

import com.test.sample.dao.StudentDao;
import com.test.sample.domain.Student;
import com.test.sample.service.StudentService;

/**
 * 单个Spring Bean测试
 *
 *
 */
@RunWith(SpringRunner.class)
public class StudentServiceTest {

    @Autowired
    StudentService studentService;

    @MockBean
    StudentDao studentDao;

    @Test
    public void test() {
        Mockito.when(studentDao.find(100)).thenReturn(new Student(100, "student100"));
        Student student = studentService.find(100);
        Assertions.assertThat(student.getName()).isEqualTo("student100");
    }

    /**
     * Spring只初始化了StudentService 这个bean，StudentService里注入的 StudentDao是通过mock生成的。
     *
     */
    @Configuration
    @Import(StudentService.class)
    static class Config {
    }

}
